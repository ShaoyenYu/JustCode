from io import StringIO, BytesIO


def string_to_bytes(buffer_string):
    buffer_bytes = BytesIO()
    buffer_bytes.writelines((x.encode() for x in buffer_string))
    return buffer_bytes


def to_csv(conn, file_path, data, index=False, header=True, encoding="utf8", **kwargs):
    """

    Args:
        conn:
        file_path:
        data: pandas.DataFrame
        **kwargs:
            overwrite: bool, default False;

    Returns:

    """

    # encoding argument in pandas.DataFrame.to_csv doesn't have effect when buffer is instance of StringIO,
    # check this: https://github.com/pandas-dev/pandas/issues/23854(opened on 22 Nov 2018 · 8 comments)
    buffer_string = StringIO()
    data.to_csv(buffer_string, index=index, header=header, encoding=encoding)
    buffer_string.seek(0)
    # conn.create(file_path, data=buffer_string, **kwargs)

    # # buffer encoded with utf-8 is necessary, since pyhdfs.HDFSClient uses latin-1(iso-8859-1)
    # # when handling TextIO instance, and this cant't be set by caller.
    # # So we encode data with utf-8 firstly, and send data in utf8-encoded-bytes directly;
    buffer_bytes = string_to_bytes(buffer_string)
    buffer_bytes.seek(0)
    conn.create(file_path, data=buffer_bytes, **kwargs)
