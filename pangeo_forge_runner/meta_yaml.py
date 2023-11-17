from traitlets import Dict, HasTraits, List, Unicode, Union


class MetaYaml(HasTraits):
    """Schema for the ``meta.yaml`` file which must be included in each feedstock directory.
    Only the ``recipes`` field is strictly required for ``pangeo-forge-runner`` to function.
    All other fields are recommended but not required.
    """

    title = Unicode(
        allow_none=True,
        help="""
        Title for this dataset.
        """,
    )
    description = Unicode(
        allow_none=True,
        help="""
        Description of the dataset.
        """,
    )
    recipes = Union(
        [List(Dict()), Dict()],
        help="""
        Specifies the deployable Python objects to run in the recipe module.
        If the recipes are assigned to their own Python variable names,
        should be of the form:

        ```yaml
        recipes:
          - id: "unique-identifier-for-recipe"
            object: "recipe:transforms"
        ```
        
        Alternatively, if the recipes are values in a Python dict:

        ```yaml
        recipes:
          dict_object: "recipe:name_of_recipes_dict"
        ```
        """,
    )
    provenance = Dict(
        allow_none=True,
        help="""
        Dataset provenance information including provider, license, etc.
        """,
        per_key_traits={
            "providers": List(
                Dict(
                    per_key_traits={
                        "name": Unicode(),
                        "description": Unicode(),
                        "roles": List(),  # TODO: enum
                        "url": Unicode(),
                    },
                ),
            ),
            "license": Unicode(),  # TODO: guidance on suggested formatting (enum?)
        },
    )
    maintainers = List(
        Dict(
            per_key_traits={
                "name": Unicode(help="Full name of the maintainer."),
                "orcid": Unicode(help="Maintainer's ORCID ID"),  # TODO: regex
                "github": Unicode(help="Maintainer's GitHub username."),
            },
        ),
        allow_none=True,
        help="""
        Maintainers of this Pangeo Forge feedstock.
        """,
    )
