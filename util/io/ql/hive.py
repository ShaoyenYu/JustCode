import pickle
from hashlib import md5
from typing import List, Dict, Union, Iterable, Optional

import numpy as np
from pyhive.exc import OperationalError
from pyhive.hive import Connection

from util.io import hdfs as hdfs_

PARTITION_SPEC = Union[Dict, List[Dict]]


def execute_hql(conn, hql, fetch=False):
    print(hql)
    with conn.cursor() as cursor:
        cursor.execute(hql)
        if fetch:
            return cursor.fetchall()


def show_tables(conn: Connection, database):
    with conn.cursor() as cursor:
        cursor.execute(f"USE `{database}`")
        cursor.execute("SHOW TABLES")
        res = cursor.fetchall()
        res = res or ()  # when  there is no table in database, fetchone return None instead of empty tuple
        res = tuple(x[0] for x in res)
    return res


def show_table_ddl(conn: Connection, database, schema):
    ddls = execute_hql(conn, f"SHOW CREATE TABLE `{database}`.`{schema}`", fetch=True)
    return ddls


def format_column_specification(columns: List):
    columns_specification = ", ".join(
        (f"`{col}` STRING COMMENT 'missing comment'" if isinstance(col, str)
         else f"`{col['name']}` {col['type']} COMMENT '{col['comment']}'" for col in columns)
    )
    return columns_specification


def create_table(conn, database, schema, columns, hive_table_dir, partitioned_by: Optional[PARTITION_SPEC] = None, **kwargs):
    """

    Args:
        conn:
        database:
        schema:
        hive_table_dir:
        columns: List[Dict]
        partitioned_by: Optional[Union[List[Dict], Dict]]
        **kwargs:
            file_format: str, valid values {
                "TEXTFILE", "SEQUENCEFILE", "ORC", "PARQUET", "AVRO", "RCFILE", "JSONFILE",
            }, default "ORC"

            for more info, please check "https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL"


    Returns:

    """
    hql_cols = format_column_specification(columns)
    hql_partions = format_partitions_spec(partitioned_by, format_type="kt") if partitioned_by else ""

    hql_create = "" \
                 "CREATE EXTERNAL TABLE IF NOT EXISTS {table} " \
                 "({cols})" \
                 "COMMENT '{comment}' " \
                 "{partitioned_by} " \
                 "ROW FORMAT {row_format} " \
                 "STORED AS {file_format} " \
                 "LOCATION '{hdfs_path}' " \
                 "".format(**{
        "table": f"`{database}`.`{schema}`",
        "cols": hql_cols,
        "comment": kwargs.get("comment", ''),
        "row_format": kwargs.get("row_format", "DELIMITED"),
        "file_format": kwargs.get("file_format", "ORC"),
        "hdfs_path": f"{hive_table_dir}/{database}/{schema}",
        "partitioned_by": hql_partions,
    })

    execute_hql(conn, hql_create)


def get_config(conn, key):
    with conn.cursor() as cursor:
        if key == "fs.default.name":
            cursor.execute("SET fs.default.name")
            value = cursor.fetchone()[0].split("fs.default.name=")[-1]
        else:
            raise NotImplementedError(f"{key} is not supported")
    return value


def get_schema_location(conn, database, schema, with_protocal=False):
    hive_tb_ddls = show_table_ddl(conn, database, schema)  # type: list[str]
    schema_file_path = hive_tb_ddls[hive_tb_ddls.index(("LOCATION",)) + 1][0].strip()[1:-1]  # remove single quote
    print(f"schema_file_path: {schema_file_path}")
    if not with_protocal:
        schema_file_path = schema_file_path.replace(get_config(conn, "fs.default.name"), "")  # Namenode URI from hadoop configuration
    return schema_file_path


def get_schema_partition_location(conn, database, schema, partitions: Dict, with_protocal=False):
    partition_descriptions = execute_hql(conn, f"DESCRIBE FORMATTED `{database}`.`{schema}` {format_partitions_spec(partitions, 'kv')}", fetch=True)
    partition_location = list(filter(lambda meta: meta[0] == "Location:           ", partition_descriptions))[0][1]

    if not with_protocal:
        protocal = get_config(conn, "fs.default.name")
        partition_location = partition_location.replace(protocal, "")
    return partition_location


def get_schema_columns(conn, database, schema):
    data = execute_hql(conn, f"DESCRIBE FORMATTED `{database}`.`{schema}`", fetch=True)
    columns_meta = data[2:data.index(('# Partition Information', None, None)) - 1]
    column_names = [column_meta[0] for column_meta in columns_meta]
    return column_names


def drop_table(conn: Connection, database, schema, purge=False, **kwargs):
    """

    Args:
        conn:
        database:
        schema:
        purge:
        **kwargs:
            conn_hdfs: HdfsClient;

    Returns:

    """

    db_tb = f"`{database}`.`{schema}`"

    if purge:
        hdfs_file_location = get_schema_location(conn, database, schema)
        print(f"drop hdfs file: {hdfs_file_location}")
        has_deleted = kwargs["conn_hdfs"].delete(hdfs_file_location, recursive=True)
        if not has_deleted:
            raise FileNotFoundError(
                f"hive schema data file on hdfs can't be found and deleted:\n"
                f"  (hdfs: {hdfs_file_location})"
            )

    execute_hql(conn, f"DROP TABLE {db_tb} {'PURGE' if purge else ''}")


def format_partitions_spec(partitions: PARTITION_SPEC, format_type, locations=None):
    """

    Args:
        partitions:
        format_type: str, valid values {"kv", "kt"}

    Returns:

    """

    def format_kv(partition: Dict, location=None):
        hql_partition = ", ".join((
            f"{k}=\'{v}\'" if isinstance(v, str) else f"{k}={v}"
            for k, v in partition.items()
        ))
        hql_part_location = f"LOCATION '{location}'" if location is not None else ""

        return f"PARTITION ({hql_partition}) {hql_part_location}"

    def format_kt(partition: Dict):
        hql_partition = ", ".join((f"{k} {v}" for k, v in partition.items()))
        return f"PARTITIONED BY ({hql_partition})"

    if format_type == "kv":
        f = format_kv
    elif format_type == "kt":
        f = format_kt
    else:
        raise NotImplementedError(f"not supported `format_type`: {format_type}")

    if isinstance(partitions, dict):
        if format_type == "kv":
            hql_partition_whole = f(partitions, locations)
        elif format_type == "kt":
            hql_partition_whole = f(partitions)

    elif isinstance(partitions, Iterable):
        if format_type == "kv":
            if locations is not None:
                assert len(partitions) == len(locations)
            hql_partition_whole = " ".join((f(par, loc) for par, loc in zip(partitions, locations)))
        elif format_type == "kt":
            hql_partition_whole = " ".join((f(par) for par in partitions))
    else:
        raise NotImplementedError(f"not supported `partitions` type: {type(partitions)}")

    return hql_partition_whole


def add_partitions(conn: Connection, database, schema, partitions: PARTITION_SPEC, locations=None):
    """

    Args:
        conn:
        database:
        schema:
        partitions: PARTITION_SPEC
            e.g.1 partitions = {"par_LogDate": "2019-01-01", "par_2": 123}
            e.g.1 partitions = [{"par_LogDate": "2019-01-01", "par_2": 123}, {"par_LogDate": "2019-01-02", "par_2": 123}]

        locations:


    Returns:

    """
    hql_partition_whole = format_partitions_spec(partitions, "kv", locations)

    hql = f"ALTER TABLE `{database}`.`{schema}` ADD IF NOT EXISTS {hql_partition_whole}"

    execute_hql(conn, hql)


def drop_partitions(conn: Connection, database, schema, partitions: PARTITION_SPEC, purge=False, **kwargs):
    # todo: 20191014: [CHANGE IMPLEMENTATION]
    #   currently we we can't purge files directly by using PURGE keyword in hive sql, it seems to be a bug, or caused
    #   by some authorization issue. So temporarily we bypassing this problem by using an additional pyhdfs session to
    #   purge files on hdfs.
    #
    # todo: 20191014: [ADD DOC]

    conn_hdfs = kwargs.get("conn_hdfs")
    if purge and conn_hdfs is not None:
        if isinstance(partitions, dict):
            partitions_ = [partitions]
        else:
            partitions_ = partitions
        for part in partitions_:
            try:
                print(conn, database, schema, part)
                partition_location_on_hdfs = get_schema_partition_location(conn, database, schema, part, with_protocal=False)
            except OperationalError as err_op:
                print("reach 1")
                # err_msg = err_op.args[0].status.infoMessages
                # if "SemanticException [Error 10006]: Partition not found" in err_msg:
                #     continue
                # else:
                #     raise err_op
                continue
            else:
                print("reach 2")
                has_deleted = conn_hdfs.delete(partition_location_on_hdfs, recursive=True)

                if not has_deleted:
                    raise FileNotFoundError(
                        f"hive schema data file on hdfs can't be found and deleted:\n"
                        f"  (hdfs: {partition_location_on_hdfs})"
                    )

    hql_partition_whole = format_partitions_spec(partitions, "kv")
    hql = f"ALTER TABLE `{database}`.`{schema}` DROP IF EXISTS {hql_partition_whole} {'PURGE' if purge else ''}"
    execute_hql(conn, hql)


def to_hive_by_ql(conn_hive, database, schema, data, partitions: Optional[PARTITION_SPEC] = None, insert_mode="overwrite"):
    """
    Args:
        schema: str
            hive table name
        data:
            data to insert
        partitions:
        insert_mode: str, valid value {"into", "overwrite"}

    Returns:

    """
    # gen cols
    hql_cols = ",".join(data.columns)
    hql_partitions = format_partitions_spec(partitions, "kv") if partitions else ""

    # gen values
    na_mask = data.isna()
    data = data.astype(str)
    data = np.where(~na_mask, "'" + data.values + "'", "null")
    data = [f'({",".join(values)})' for values in data]
    hql_values = ",".join(data)

    if insert_mode == "into":
        hql_insert = f"INSERT INTO TABLE `{database}`.`{schema}` {hql_partitions} ({hql_cols}) VALUES {hql_values}"
    elif insert_mode == "overwrite":
        hql_insert = f"INSERT OVERWRITE TABLE `{database}`.`{schema}` {hql_partitions}  VALUES {hql_values}"
    else:
        raise NotImplementedError

    execute_hql(conn_hive, hql_insert, False)


def to_hive_by_csv(conn_hive, conn_hdfs, database, schema, data, partitions: Optional[PARTITION_SPEC] = None, insert_mode="overwrite"):
    # to avoid column mismatch, we get columns of schema, and reindex data before generating csv file
    data = data.reindex(columns=get_schema_columns(conn_hive, database, schema))
    signature = md5(pickle.dumps(data)).hexdigest()

    location_schema = get_schema_location(conn_hive, database, schema)
    partition_directory = ",".join(f"{k}={v}" for k, v in partitions.items())
    location_partition = f"{location_schema}/{partition_directory}"

    if insert_mode == "overwrite":
        drop_partitions(conn_hive, database, schema, partitions=partitions, conn_hdfs=conn_hdfs, purge=True)
    hdfs_.to_csv(conn_hdfs, f"{location_partition}/{signature}", data, index=False, header=False, overwrite=True)
    add_partitions(conn_hive, database, schema, partitions=partitions, locations=location_partition)
