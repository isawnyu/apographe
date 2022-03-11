#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define base Query class
"""


class Query:
    def __init__(self):
        self.parameters = dict()
        self._supported_parameters = dict()
        self._default_web_parameters = dict()

    @property
    def supported_parameters(self):
        """List supported parameters"""
        return list(self._supported_parameters.keys())

    def clear_parameters(self):
        """Reset all parameters for the query."""
        self.parameters = dict()

    @property
    def parameters_for_web(self):
        p = dict()
        for k, v in self._default_web_parameters.items():
            p[k] = v
        for k, v in self.parameters.items():
            these_web_params = self._convert_for_web(k, *v)
            for webk, webv in these_web_params.items():
                p[webk] = webv
        return p

    def set_parameter(self, name, value, operator=None):
        """Set a single parameter on the query."""
        try:
            rules = self._supported_parameters[name]
        except KeyError:
            raise ValueError(
                f"Unexpected parameter name '{name}'. Supported parameters: {sorted(self.supported_parameters)}."
            )
        if not isinstance(value, rules["expected"]):
            raise TypeError(
                f"Unexpected type {type(value)} for parameter '{name}'. Expected type(s): {rules['expected']}."
            )
        self.parameters[name] = (value, operator)

    def _convert_for_web(self, name, value, operator):
        """Convert our generic parameters to the specific ones Pleiades uses"""
        web_params = dict()
        rules = self._supported_parameters[name]

        # determine parameter name (key) to use in web query
        try:
            newname = rules["rename"]
        except KeyError:
            cooked_key = name
        else:
            cooked_key = newname

        # pre-process web parameters to meet query interface expectations
        try:
            preprocess_func = rules["behavior"]
        except KeyError:
            if isinstance(value, list):
                try:
                    behavior = rules["list_behavior"]
                except KeyError:
                    cooked_value = " ".join(value)
                else:
                    if behavior == "list":
                        cooked_key = ":".join((cooked_key, "list"))
                        cooked_value = ",".join(value)
                    elif behavior == "join":
                        if operator:
                            cooked_value = f" {operator} ".join(value)
                        else:
                            cooked_value = " ".join(value)
                    elif behavior == "noseq":
                        cooked_value = (
                            value  # assumes urlencode will be applied with noseq=True
                        )
                    else:
                        raise ValueError(behavior)
                try:
                    additional = rules["list_additional"][operator]
                except KeyError:
                    pass
                else:
                    for add_k, add_v in additional.items():
                        web_params[add_k] = add_v
            elif isinstance(value, str):
                cooked_value = value
            else:
                raise TypeError(type(value))
            web_params[cooked_key] = cooked_value
        else:
            these_params = preprocess_func(value)
            for this_k, this_v in these_params.items():
                web_params[this_k] = this_v
        return web_params
