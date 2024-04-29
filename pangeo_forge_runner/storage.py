from dataclasses import fields

from fsspec import AbstractFileSystem
from traitlets import Dict, Type, Unicode, Bool
from traitlets.config import LoggingConfigurable


class StorageTargetConfig(LoggingConfigurable):
    """
    Configuration for Storage Targets when a Pangeo Forge recipe is baked
    """

    fsspec_class = Type(
        klass=AbstractFileSystem,
        config=True,
        help="""
        FSSpec Filesystem to instantiate as class for this target
        """,
    )

    fsspec_args = Dict(
        {},
        config=True,
        help="""
        Args to pass to fsspec_class during instantiation
        """,
    )

    root_path = Unicode(
        "",
        config=True,
        help="""
        Root path under which to put all our storage.

        If {job_name} is present in the root_path, it will be expanded to the
        unique job_name of the current job.
        """,
    )

    enable_assume_role = Bool(
        False,
        config=True,
        help="""
        Whether to enable assuming roles when inside running jobs 
        'pangeo_forge_recipes.storage.FSSpecTarget.fsspec_kwargs' is accessed
        """,
    )

    assume_role_credential_kwargs = Dict(
        {},
        config=True,
        help="""
        kwargs (default {}) to call 'aws sts --assume-role' role with 
        such as '{"RoleArn": str, "RoleSessionName": str, "DurationSeconds: int}'
        """,
    )

    pangeo_forge_target_class = Unicode(
        config=False,
        help="""
        Name of StorageConfig class from pangeo_forge_recipes to instantiate.

        Should be set by subclasses.
        """,
    )

    def is_default(self):
        """
        Return if `root_path` is an empty string

        `.root_path` is an empty string by default. For optional storage targets,
        this is used to mean it's unconfigured.
        """
        return self.fsspec_class == AbstractFileSystem and not self.root_path

    def get_forge_target(self, job_name: str):
        """
        Return correct pangeo-forge-recipes Target

        If {job_name} is present in `root_path`, it is expanded with the given job_name
        """
        # import dynamically on call, because different versions of `pangeo-forge-recipes.storage`
        # contain different objects, so a static top-level import cannot be used.
        from pangeo_forge_recipes import storage

        cls = getattr(storage, self.pangeo_forge_target_class)

        # pangeo-forge-recipes >=0.10.3 have a new `enable_assume_role` kwarg
        if any(field.name == "enable_assume_role" for field in fields(cls)):
            return cls(
                self.fsspec_class(**self.fsspec_args),
                root_path=self.root_path.format(job_name=job_name),
                _fsspec_kwargs=self.fsspec_args,
                enable_assume_role=self.enable_assume_role,
                assume_role_credential_kwargs=self.assume_role_credential_kwargs
            )
        # pangeo-forge-recipes 0.10.5,<0.10.3 have a new `fsspec_kwargs` kwarg
        elif any(field.name == "fsspec_kwargs" for field in fields(cls)):
            return cls(
                self.fsspec_class(**self.fsspec_args),
                root_path=self.root_path.format(job_name=job_name),
                fsspec_kwargs=self.fsspec_args,
            )
        else:
            return cls(
                self.fsspec_class(**self.fsspec_args),
                root_path=self.root_path.format(job_name=job_name),
            )

    def __str__(self):
        """
        Return sanitized string representation, stripped of possible secrets
        """
        # Only show keys and type of values of args to fsspec, as they might contain secrets
        fsspec_args_filtered = ", ".join(
            f"{k}=<{type(v).__name__}>" for k, v in self.fsspec_args.items()
        )
        return f'{self.pangeo_forge_target_class}({self.fsspec_class.__name__}({fsspec_args_filtered}, root_path="{self.root_path}")'


class InputTargetStorage(StorageTargetConfig):
    """
    Storage configuration for where the baked data should be stored
    """

    pangeo_forge_target_class = "FSSpecInputTarget"


class TargetStorage(StorageTargetConfig):
    """
    Storage configuration for where the baked data should be stored
    """

    pangeo_forge_target_class = "FSSpecTarget"


class InputCacheStorage(StorageTargetConfig):
    """
    Storage configuration for caching input files during recipe baking
    """

    pangeo_forge_target_class = "CacheFSSpecTarget"
