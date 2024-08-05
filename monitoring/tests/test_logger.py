import pytest
from unittest.mock import MagicMock

from monitoring import Logger, LogTypeEnum


class TestLogger:

    @pytest.fixture
    def observer(self):
        return MagicMock()

    @pytest.fixture
    def logger(self):
        return Logger()
    
    def test_should_raise_exception_when_trying_to_subscribe_with_at_least_one_invalid_log_type(
        self, observer: MagicMock, logger: Logger
    ):
        with pytest.raises(ValueError):
            logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum("invalid")])

    def test_should_subscribe_an_observer_for_the_correct_log_types(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.INFO])

        assert observer in logger._observers[LogTypeEnum.SUCCESS]
        assert observer in logger._observers[LogTypeEnum.INFO]

    def test_should_not_subscribe_an_observer_for_not_specified_log_types(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.INFO])

        assert observer not in logger._observers[LogTypeEnum.WARNING]
        assert observer not in logger._observers[LogTypeEnum.ERROR]
        assert observer not in logger._observers[LogTypeEnum.DEBUG]

    def test_should_not_subscribe_an_observer_twice_for_the_same_log_type(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.SUCCESS])
        logger.subscribe(observer, [LogTypeEnum.SUCCESS])

        assert len(logger._observers[LogTypeEnum.SUCCESS]) == 1

    def test_should_raise_exception_when_trying_to_unsubscribe_with_at_least_one_invalid_log_type(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS])

        with pytest.raises(ValueError):
            logger.unsubscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum("invalid")])

    def test_should_unsubscribe_an_observer_for_the_correct_log_types(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.INFO])
        logger.unsubscribe(observer, [LogTypeEnum.SUCCESS])

        assert observer not in logger._observers[LogTypeEnum.SUCCESS]

    def test_should_not_unsubscribe_an_observer_for_not_specified_log_types(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.INFO])
        logger.unsubscribe(observer, [LogTypeEnum.SUCCESS])

        assert observer in logger._observers[LogTypeEnum.INFO]

    def test_should_not_unsubscribe_an_observer_that_was_not_subscribeed(
        self, observer: MagicMock, logger: Logger
    ):
        logger.unsubscribe(observer, [LogTypeEnum.SUCCESS])

        assert observer not in logger._observers[LogTypeEnum.SUCCESS]

    @pytest.mark.parametrize(
        "log_type",
        [
            LogTypeEnum.SUCCESS,
            LogTypeEnum.INFO,
            LogTypeEnum.WARNING,
            LogTypeEnum.ERROR,
            LogTypeEnum.DEBUG,
        ],
    )
    def test_should_raise_exception_when_subscribeing_an_observer_for_log_type_if_it_doesnt_have_the_method(
        self,
        log_type: LogTypeEnum,
        observer: MagicMock,
        logger: Logger,
    ):
        delattr(observer, f"on_{log_type.value.lower()}")

        with pytest.raises(AttributeError):
            logger.subscribe(observer, [log_type])

    def test_should_subscribe_an_observer_if_it_has_the_method_for_the_log_type_but_not_for_all(
        self, observer: MagicMock, logger: Logger
    ):
        observer.on_success = None
        observer.on_warning = None
        observer.on_error = None
        observer.on_debug = None

        logger.subscribe(observer, [LogTypeEnum.INFO])

        assert observer in logger._observers[LogTypeEnum.INFO]

    def test_should_raise_exception_when_trying_to_notify_for_invalid_log_type(
        self, logger: Logger
    ):
        with pytest.raises(ValueError):
            logger.notify("message", LogTypeEnum("invalid"))

    @pytest.mark.parametrize(
        "log_type",
        [
            LogTypeEnum.SUCCESS,
            LogTypeEnum.INFO,
            LogTypeEnum.WARNING,
            LogTypeEnum.ERROR,
            LogTypeEnum.DEBUG,
        ],
    )
    def test_should_notify_all_observers_for_the_correct_log_type(
        self,
        log_type: LogTypeEnum,
        logger: Logger,
    ):
        observer1 = MagicMock()
        observer2 = MagicMock()
        logger.subscribe(observer1, [log_type])
        logger.subscribe(observer2, [log_type])

        # Act
        logger.notify("message", log_type)

        # Assert
        method_name = log_type.value.lower()
        if log_type == LogTypeEnum.ERROR:
            getattr(observer1, f"on_{method_name}").assert_called_once_with(
                "message", None
            )
            getattr(observer2, f"on_{method_name}").assert_called_once_with(
                "message", None
            )
        else:
            getattr(observer1, f"on_{method_name}").assert_called_once_with("message")
            getattr(observer2, f"on_{method_name}").assert_called_once_with("message")

    def test_should_not_notify_observers_for_log_types_that_they_dont_subscribed_for(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS])

        logger.notify("message", LogTypeEnum.INFO)

        observer.on_success.assert_not_called()

    def test_should_not_notify_observers_that_have_been_unsubscribeed_for_a_specific_log_type(
        self, observer: MagicMock, logger: Logger
    ):
        logger.subscribe(observer, [LogTypeEnum.SUCCESS, LogTypeEnum.INFO])
        logger.unsubscribe(observer, [LogTypeEnum.SUCCESS])

        logger.notify("message", LogTypeEnum.SUCCESS)
        logger.notify("message", LogTypeEnum.INFO)

        observer.on_success.assert_not_called()
        observer.on_info.assert_called_once_with("message")
