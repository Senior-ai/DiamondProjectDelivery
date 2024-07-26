import csv
import io
from abc import ABC
from typing import Union, Callable
from urllib.parse import urlparse

type ErrorMessage = str


class ValidatedValue:
    _simple_error_message = 'Value "{value}" is not valid.'
    _error_message_with_position = 'Value "{value}" is not valid in row {row}, column "{column}".'

    @property
    def is_valid(self) -> bool:
        return self.__is_valid

    def get_error_message(self, gettext: callable) -> ErrorMessage | None:
        if self.__is_valid:
            return None

        if self.__row is None or self.__column is None:
            error_message = gettext(self._simple_error_message)
            return error_message.format(value=self.__value)

        error_message = gettext(self._error_message_with_position)
        return error_message.format(value=self.__value, row=self.__row, column=self.__column)

    def set_position(self, row: int, column: str) -> None:
        if not isinstance(row, int):
            raise TypeError
        if not isinstance(column, str):
            raise TypeError

        self.__row = row
        self.__column = column

    def __init__(self, value: str, is_valid: bool):
        if not isinstance(value, str):
            raise TypeError
        if not isinstance(is_valid, bool):
            raise TypeError

        self.__value: str = value
        self.__is_valid: bool = is_valid
        self.__row: int | None = None
        self.__column: str | None = None


class ValidatedNumeric(ValidatedValue):
    _simple_error_message = 'Value "{value}" is not numeric.'
    _error_message_with_position = 'Value "{value}" is not numeric in row {row}, column "{column}".'


class ValidatedInteger(ValidatedValue):
    _simple_error_message = 'Value "{value}" is not an integer.'
    _error_message_with_position = 'Value "{value}" is not an integer in row {row}, column "{column}".'


class ValidatedText(ValidatedValue):
    _simple_error_message = 'Any text value expected.'
    _error_message_with_position = 'Any text value expected in row {row}, column "{column}".'


class ValidatedMeasurements(ValidatedValue):
    _simple_error_message = 'Value "{value}" is not a measurements.'
    _error_message_with_position = 'Value "{value}" is not a valid measurements in row {row}, column "{column}".'


class ValidatedLiteral(ValidatedValue):
    _simple_error_message = 'Value "{value}" is not a valid option.'
    _error_message_with_position = 'Value "{value}" is not a valid option in row {row}, column "{column}".'


class ValidatedURL(ValidatedValue):
    _simple_error_message = 'Value "{value}" is not a valid URL.'
    _error_message_with_position = 'Value "{value}" is not a valid URL in row {row}, column "{column}".'


class ValueValidator(ABC):
    def validate(self, value: str) -> ValidatedValue:
        ...


class NumericValidator(ValueValidator):
    def validate(self, value: str) -> ValidatedValue:
        try:
            float(value)
        except ValueError:
            return ValidatedNumeric(value, False)
        else:
            return ValidatedNumeric(value, True)


class IntegerValidator(ValueValidator):
    def validate(self, value: str) -> ValidatedValue:
        try:
            int(value)
        except ValueError:
            return ValidatedInteger(value, False)
        else:
            return ValidatedInteger(value, True)


class NotEmptyTextValidator(ValueValidator):
    def validate(self, value: str) -> ValidatedValue:
        if not isinstance(value, str):
            raise TypeError
        if value == "":
            return ValidatedText(value, False)
        return ValidatedText(value, True)


class MeasurementsValidator(ValueValidator):
    def validate(self, value: str) -> ValidatedValue:
        try:
            measurement1, other = value.split(" - ")
            measurement2, measurement3 = other.split(" x ")
        except ValueError:
            return ValidatedMeasurements(value, False)

        try:
            float(measurement1)
            float(measurement2)
            float(measurement3)
        except ValueError:
            return ValidatedMeasurements(value, False)
        return ValidatedMeasurements(value, True)


class NullableValidator(ValueValidator):
    def __init__(self, value_validator: ValueValidator):
        self.__value_validator = value_validator

    def validate(self, value: str) -> ValidatedValue:
        if value == "":
            return ValidatedValue(value, True)
        return self.__value_validator.validate(value)


class LiteralValidator(ValueValidator):
    def __init__(self, literals: list[str]):
        if not all(isinstance(literal, str) for literal in literals):
            raise TypeError

        self.__literals = literals

    def validate(self, value: str) -> ValidatedValue:
        if value not in self.__literals:
            return ValidatedLiteral(value, False)
        return ValidatedLiteral(value, True)


class URLValidator(ValueValidator):
    def validate(self, value: str) -> ValidatedValue:
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return ValidatedURL(value, False)
        except:
            return ValidatedURL(value, False)
        return ValidatedURL(value, True)


class CSVValidator:
    @staticmethod
    def __default_gettext(message: str) -> str:
        return message

    def __check_header(self,
                       reader: csv.DictReader,
                       gettext: Callable[[str], str],
                       ignore_extra_columns: bool = False) -> list[ErrorMessage]:
        header_errors: list[ErrorMessage] = []

        if reader.fieldnames is None and self.columns:
            header_errors.append(gettext("No csv file header found."))
            return header_errors

        missing_columns = [col for col in self.columns.keys() if col not in reader.fieldnames]
        if missing_columns:
            error_message = gettext('Missing column(s) in csv file header: {missing_columns}')
            header_errors.append(error_message.format(missing_columns=", ".join(missing_columns)))

        if not ignore_extra_columns:
            extra_columns = [col for col in reader.fieldnames if col not in self.columns.keys()]
            if extra_columns:
                error_message = gettext('Extra columns found in csv file header: {extra_columns}')
                header_errors.append(error_message.format(extra_columns=", ".join(extra_columns)))

        return header_errors

    def validate(self,
                 file: io.TextIOWrapper,
                 gettext: Union[Callable[[str], str], None] = None,
                 ignore_extra_column: bool = False) -> list[ErrorMessage]:
        if gettext is None:
            gettext = self.__default_gettext

        try:
            reader = csv.DictReader(file, delimiter=",")

            if header_errors := self.__check_header(reader, gettext, ignore_extra_column):
                return header_errors

            for row_number, row in enumerate(reader, start=1):
                validated_values = []
                for column_name, value_checkers in self.columns.items():
                    value = row.get(column_name, "")

                    for value_checker in value_checkers:
                        validated_value = value_checker.validate(value)
                        validated_value.set_position(row_number, column_name)
                        validated_values.append(validated_value)
                if any(not validated_value.is_valid for validated_value in validated_values):
                    invalid_values = filter(lambda validated_value: not validated_value.is_valid, validated_values)
                    return [validated_value.get_error_message(gettext) for validated_value in invalid_values]
        except csv.Error:
            return [gettext("Invalid csv file format.")]

        return []

    def add_column(self, name: str, value_checkers: list[ValueValidator]):
        self.columns[name] = value_checkers

    def __init__(self):
        self.columns: dict[str, list[ValueValidator]] = {}
