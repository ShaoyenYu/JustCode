import sys
import pymysql
import re
import time

__author__ = "Yu<shaoyenyu@gmail.com>"


def sql_cols(df, usage="sql"):
    cols = tuple(df.columns)
    if usage == "sql":
        cols_str = str(cols).replace("'", "`")
        if len(df.columns) == 1:
            cols_str = cols_str[:-2] + ")"  # to process dataframe with only one column
        return cols_str
    elif usage == "format":
        base = "'%%(%s)s'" % cols[0]
        for col in cols[1:]:
            base += ", '%%(%s)s'" % col
        return base
    elif usage == "values":
        base = "%s=VALUES(%s)" % (cols[0], cols[0])
        for col in cols[1:]:
            base += ", `%s`=VALUES(`%s`)" % (col, col)
        return base


def to_sql(tb_name: str, conn, dataframe, type: str = "update", chunksize: int = 2000, debug: bool = False):
    """
    Dummy of pandas.to_sql, support "REPLACE INTO ..." and "INSERT ... ON DUPLICATE KEY UPDATE (keys) VALUES (values)"
    SQL statement.

    Args:
        tb_name: str
            Table to insert data;
        conn:
            DBAPI Instance, could be a engine, or a connection
        dataframe: pandas.DataFrame
            Dataframe instance
        type: str, optional value {"update", "replace", "ignore"}, default "update"
            Update method:
            "update" -> "INSERT ... ON DUPLICATE UPDATE ..." SQL statement;
            "replace" -> "REPLACE ..." SQL statement;
            "ignore" -> "INSERT IGNORE ..." SQL statement;
        chunksize: int
            Size of records to be inserted each time;
        debug: bool, default False
            don't use, will be deprecated in future

    """

    tb_name = ".".join([f"`{x}`" for x in tb_name.split(".")])

    df = dataframe.copy()
    # todo 20180922 can directly fillna with NULL, need to add test
    df = df.fillna("None")
    df = df.applymap(lambda x: re.sub('([\'\"\\\])', '\\\\\g<1>', str(x)))
    cols_str = sql_cols(df)
    sqls = []
    for i in range(0, len(df), chunksize):
        df_tmp = df[i: i + chunksize]

        if type == "replace":
            sql_base = "REPLACE INTO {tb_name} {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )

        elif type == "update":
            sql_base = "INSERT INTO {tb_name} {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )
            sql_update = "ON DUPLICATE KEY UPDATE {0}".format(
                sql_cols(df_tmp, "values")
            )

        elif type == "ignore":
            sql_base = "INSERT IGNORE INTO {tb_name} {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )

        sql_val = sql_cols(df_tmp, "format")
        vals = tuple([sql_val % x for x in df_tmp.to_dict("records")])
        sql_vals = "VALUES ({x})".format(x=vals[0])
        for i in range(1, len(vals)):
            sql_vals += ", ({x})".format(x=vals[i])
        sql_vals = sql_vals.replace("'None'", "NULL")

        sql_main = sql_base + sql_vals
        if type == "update":
            sql_main += sql_update

        if sys.version_info.major == 2:
            sql_main = sql_main.replace("u`", "`")
        if sys.version_info.major == 3:
            sql_main = sql_main.replace("%", "%%")

        if debug is False:
            try:
                conn.execute(sql_main)
            except pymysql.err.InternalError as e:
                print("ENCOUNTERING ERROR: {e}, RETRYING".format(e=e))
                time.sleep(10)
                conn.execute(sql_main)
        else:
            sqls.append(sql_main)
    if debug:
        return sqls


def delete(tb_name, conn, dataframe, chunksize=10000):
    """

    Args:
        tb_name:
        conn:
        dataframe:
        chunksize:

    Returns:

    """

    dataframe = dataframe.dropna()
    for i in range(0, len(dataframe), chunksize):
        df = dataframe[i: i + chunksize]
        condition = generate_condition(df)
        sql = "DELETE FROM {tb} WHERE ({criterion})".format(
            tb=tb_name, criterion=condition
        )
        conn.execute(sql)


def generate_condition(dataframe):
    dataframe = dataframe.dropna()
    cols = dataframe.columns
    if len(cols) == 1:
        tmp = str(tuple(dataframe[cols[0]].apply(lambda x: str(x)).tolist()))
        if len(dataframe) == 1:
            tmp = tmp[:-2] + ")"
        condition = "{col} IN {val}".format(col=cols[0], val=tmp)
    else:
        s = ""
        for i, col in enumerate(cols):
            if i > 0:
                s += " AND `{k}` = ".format(k=col) + "'{" + str(i) + "}'"
            else:
                s = "`{k}` = ".format(k=col) + "'{" + str(i) + "}'"
        s = "(" + s + ")"
        conditions = []
        for val in dataframe.as_matrix():
            tmp = s.format(*val)
            conditions.append(tmp)

        condition = " OR ".join(conditions)
    return condition
