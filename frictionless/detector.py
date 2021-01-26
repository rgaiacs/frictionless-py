from copy import copy, deepcopy
from .exception import FrictionlessException
from .schema import Schema
from .field import Field
from . import helpers
from . import errors
from . import config


class Detector:
    def __init__(
        self,
        byte_volume=config.DEFAULT_BYTE_VOLUME,
        data_volume=config.DEFAULT_DATA_VOLUME,
        encoding_guesser=None,
        encoding_confidence=config.DEFAULT_ENCODING_CONFIDENCE,
        field_type=None,
        field_names=None,
        field_confidence=config.DEFAULT_FIELD_CONFIDENCE,
        field_float_numbers=config.DEFAULT_FLOAT_NUMBERS,
        field_missing_values=config.DEFAULT_MISSING_VALUES,
        schema_sync=False,
        schema_patch=None,
    ):
        self.__byte_volume = byte_volume
        self.__data_volume = data_volume
        self.__encoding_guesser = encoding_guesser
        self.__encoding_confidence = encoding_confidence
        self.__field_type = field_type
        self.__field_names = field_names
        self.__field_confidence = field_confidence
        self.__field_float_numbers = field_float_numbers
        self.__field_missing_values = field_missing_values
        self.__schema_sync = schema_sync
        self.__schema_patch = schema_patch

    @property
    def byte_volume(self):
        return self.__byte_volume

    @property
    def data_volume(self):
        return self.__data_volume

    # Detect

    def detect_encoding(self, sample):
        """Detect encoding from sample

        Parameters:
            sample (byte): byte sample

        Returns:
            str: encoding
        """
        if self.__encoding_guesser:
            return self.__encoding_guesser(sample)
        return helpers.detect_encoding(sample)

    # TODO: implement
    def detect_layout(self, sample):
        """Detect layout from sample

        Parameters:
            sample (any[][]): data sample

        Returns:
            Layout: layout
        """
        pass

    def detect_schema(self, sample, *, labels=None, schema=None):
        """Detect schema from sample

        Parameters:
            sample (any[][]): data sample
            labels? (str[]): data labels
            schema? (Schema): data schema

        Returns:
            Schema: schema
        """

        # Create schema
        if not schema or not schema.fields:
            schema = Schema()

            # Missing values
            if self.__field_missing_values != config.DEFAULT_MISSING_VALUES:
                schema.missing_values = self.__field_missing_values

            # Prepare names
            names = copy(self.__field_names or labels or [])
            if not names:
                if not sample:
                    return schema
                names = [f"field{number}" for number in range(1, len(sample[0]) + 1)]

            # Handle name/empty
            for index, name in enumerate(names):
                names[index] = name or f"field{index+1}"

            # Deduplicate names
            if len(names) != len(set(names)):
                seen_names = []
                names = names.copy()
                for index, name in enumerate(names):
                    count = seen_names.count(name) + 1
                    names[index] = "%s%s" % (name, count) if count > 1 else name
                    seen_names.append(name)

            # Handle type/empty
            if self.__field_type or not sample:
                type = self.__field_type
                schema.fields = [{"name": name, "type": type or "any"} for name in names]
                return schema

            # Prepare fields
            runners = []
            max_score = [len(sample)] * len(names)
            for index, name in enumerate(names):
                runners.append([])
                for type in FIELD_TYPES:
                    field = Field(name=name, type=type, schema=schema)
                    if type == "number" and self.__field_float_numbers:
                        field.float_number = True
                    runners[index].append({"field": field, "score": 0})
                schema.fields.append(Field(name=name, type="any", schema=schema))

            # Infer fields
            for cells in sample:
                for index, name in enumerate(names):
                    if schema.fields[index].type != "any":
                        continue
                    source = cells[index] if len(cells) > index else None
                    if source in self.__field_missing_values:
                        max_score[index] -= 1
                        continue
                    for runner in runners[index]:
                        if runner["score"] < len(sample) * (self.__field_confidence - 1):
                            continue
                        target, notes = runner["field"].read_cell(source)
                        runner["score"] += 1 if not notes else -1
                        if runner["score"] >= max_score[index] * self.__field_confidence:
                            schema.fields[index] = runner["field"]
                            break

        # Sync schema
        if self.__schema_sync:
            if labels:
                fields = []
                mapping = {field.get("name"): field for field in schema.fields}
                for name in labels:
                    fields.append(mapping.get(name, {"name": name, "type": "any"}))
                schema.fields = fields

        # Patch schema
        if self.__schema_patch:
            schema_patch = deepcopy(self.__schema_patch)
            fields = schema_patch.pop("fields", {})
            schema.update(schema_patch)
            for field in schema.fields:
                field.update((fields.get(field.get("name"), {})))

        # Validate schema
        # TODO: reconsider this - not perfect for transform
        if len(schema.field_names) != len(set(schema.field_names)):
            note = "Schemas with duplicate field names are not supported"
            raise FrictionlessException(errors.SchemaError(note=note))

        return schema


# Internal

FIELD_TYPES = [
    "yearmonth",
    "geopoint",
    "duration",
    "geojson",
    "object",
    "array",
    "datetime",
    "time",
    "date",
    "integer",
    "number",
    "boolean",
    "year",
    "string",
]