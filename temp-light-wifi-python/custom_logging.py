import sys
import time

ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10

_level_dict = {
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_loggers = {}
_default_fmt = "%(asctime)s - %(levelname)s:%(name)s:%(message)s"
_default_datefmt = "%Y-%m-%d %H:%M:%S"


class LogRecord:
    def set(self, name, level, message):
        self.name = name
        self.levelno = level
        self.levelname = _level_dict[level]
        self.message = message
        self.ct = time.time()
        self.msecs = int((self.ct - int(self.ct)) * 1000)
        self.asctime = None


class Formatter:
    def __init__(self, fmt=_default_fmt, datefmt=_default_datefmt):
        self.fmt = fmt
        self.datefmt = datefmt

    def usesTime(self):
        return "asctime" in self.fmt

    def formatTime(self, datefmt, record):
        year, month, mday, hour, minute, second, _, _ = time.localtime(record.ct)
        codes = {
            "%Y": f"{year:04d}",
            "%m": f"{month:02d}",
            "%d": f"{mday:02d}",
            "%H": f"{hour:02d}",
            "%M": f"{minute:02d}",
            "%S": f"{second:02d}",
        }
        result = datefmt
        for code, value in codes.items():
            result = result.replace(code, value)
        return result

    def format(self, record):
        if self.usesTime():
            record.asctime = self.formatTime(self.datefmt, record)
        return self.fmt % {
            "name": record.name,
            "message": record.message,
            "msecs": record.msecs,
            "asctime": record.asctime,
            "levelname": record.levelname,
        }


class Handler:
    def __init__(self, level, formatter):
        self.level = level
        self.formatter = formatter

    def close(self):
        pass

    def setLevel(self, level):
        self.level = level

    def setFormatter(self, formatter: Formatter):
        self.formatter = formatter

    def format(self, record):
        return self.formatter.format(record)

    def emit(self, record):
        raise NotImplementedError("emit() must be implemented by subclasses.")


class StreamHandler(Handler):
    def __init__(self, stream, level, formatter):
        super().__init__(level=level, formatter=formatter)
        self.stream = stream
        self.terminator = "\n"

    def close(self):
        if hasattr(self.stream, "flush"):
            self.stream.flush()

    def emit(self, record):
        if record.levelno >= self.level:
            self.stream.write(self.format(record) + self.terminator)


class FileHandler(StreamHandler):
    def __init__(self, level, formatter, filename, mode="a", encoding="UTF-8"):
        super().__init__(
            stream=open(filename, mode=mode, encoding=encoding),
            level=level,
            formatter=formatter,
        )

    def close(self):
        super().close()
        self.stream.close()


class Logger:
    def __init__(self, name, level, file):
        self.name = name
        self.file = file
        self.level = level
        self.handlers: list[Handler] = []
        self.record = LogRecord()

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level)

    def log(self, level, msg, *args):
        if self.isEnabledFor(level):
            if args:
                if isinstance(args[0], dict):
                    args = args[0]
                msg = msg % args
            if self.handlers:
                for h in self.handlers:
                    self.record.set(self.name, level, msg)
                    h.emit(self.record)
            else:
                print(
                    _level_dict[level], ":", self.name, ":", msg, sep="", file=self.file
                )

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def addHandler(self, handler: Handler):
        self.handlers.append(handler)

    def hasHandlers(self):
        return len(self.handlers) > 0


def getLogger(name="root"):
    if name not in _loggers:
        if "root" in _loggers:
            root_logger = _loggers["root"]
            _loggers[name] = Logger(name, root_logger.level, root_logger.file)
            for h in root_logger.handlers:
                _loggers[name].addHandler(h)
        else:
            _loggers[name] = Logger(name, DEBUG, sys.stderr)
    return _loggers[name]


def log(level, msg, *args):
    getLogger().log(level, msg, *args)


def debug(msg, *args):
    getLogger().debug(msg, *args)


def info(msg, *args):
    getLogger().info(msg, *args)


def warning(msg, *args):
    getLogger().warning(msg, *args)


def shutdown():
    for k, logger in _loggers.items():
        for h in logger.handlers:
            h.close()
        _loggers.pop(logger, None)


def basicConfig(
    filename=None,
    filemode="a",
    format=_default_fmt,
    datefmt=_default_datefmt,
    level=WARNING,
    stream=sys.stderr,
    encoding="UTF-8",
    force=False,
):
    if "root" not in _loggers:
        _loggers["root"] = Logger("root", level, stream)

    logger = _loggers["root"]

    if force or not logger.handlers:
        for logger in _loggers.values():
            for h in logger.handlers:
                h.close()
            logger.handlers.clear()

        if filename is None:
            handler = StreamHandler(stream, level, Formatter(format, datefmt))
        else:
            handler = FileHandler(
                level, Formatter(format, datefmt), filename, filemode, encoding
            )

        handler.setLevel(level)
        handler.setFormatter(Formatter(format, datefmt))

        for logger in _loggers.values():
            logger.addHandler(handler)
