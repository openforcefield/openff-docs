# Installation

OpenFF software is distributed via [Conda Forge], a repository of software packages maintained by the open source community. You need a Conda-compatible package manager to install Conda Forge software. OpenFF recommends [Mamba], installed via the [MambaForge] distribution.

[Conda Forge]: https://conda-forge.org/
[Mamba]: inv:mamba#index
[MambaForge]: https://github.com/conda-forge/miniforge#user-content-mambaforge

(quick_install)=
## Quick Install Guide

This guide describes how to install OpenFF software within your own user account. Note that this does not require sudo/root access.

:::{admonition} Existing Conda/Mamba Installations
If you have an existing Mamba installation, skip steps 1 and 2 below. If you have an existing Conda installation, see [](existing_conda).
:::

1. Download the appropriate MambaForge installer from the [MambaForge repository]. Use [Mambaforge-MacOSX-x86_64] on a Mac and [Mambaforge-Linux-x86_64] on Linux/WSL.

2. Run the MambaForge installer in a terminal window and accept the license agreement: 

    ```shell-session
    $ bash Mambaforge-$(uname)-x86_64.sh
    ```

    1.  When asked for an install destination, choose a directory owned by your user account (such as the default).

    2. When asked if you'd like to initialize MambaForge, answer "yes". Note that this will modify your shell's startup script; for more information about this choice, see [](conda_init). 

    3. Once the installer is finished, close the window and run the following command in a new terminal window: 

        ```shell-session
        $ conda config --set auto_activate_base false
        ```

3. Close and reopen the terminal window and install the desired packages into a [new environment]. The names of OpenFF packages can be found in the [projects list]: 
    ```shell-session
    $ mamba create -c conda-forge -n openff openff-toolkit-examples
    ```

4. To use a package, first activate the environment, then run the desired command. Activation lasts until you close the shell session. For example, run the Toolkit Showcase example:

    ```shell-session
    $ conda activate openff
    $ openff-toolkit-examples --target offtk-examples
    $ cd offtk-examples/toolkit_showcase
    $ jupyter-lab toolkit_showcase.ipynb
    ```

If that worked, you're all set! The rest of this page covers corner cases and how to manage Conda environments. For package-specific installation instructions, please see the individual [project docs].

:::{admonition} OpenFF on Windows
We recommend installing MambaForge through WSL on Windows. For more information, see [](install_windows).
:::

:::{admonition} OpenFF on Apple Silicon
If you run into issues with upstream dependencies not supporting Apple Silicon, we recommend installing x86_64 MambaForge. For more information, see [](install_arm).
:::

[MambaForge repository]: https://github.com/conda-forge/miniforge#user-content-mambaforge
[Mambaforge-MacOSX-x86_64]: https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-x86_64.sh
[Mambaforge-Linux-x86_64]: https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh

[new environment]: managing_environments
[projects list]: projects
[project docs]: projects

* * *

(install_mamba)=
## Installing Mamba

Mamba is a drop-in replacement for the Conda package manager. It is faster and can sometimes find ways to safely install two pieces of software that Conda thinks have conflicting dependencies. MambaForge includes Mamba itself, as well as an initial configuration supporting Conda Forge.

If you don't have Conda or Mamba installed, installing MambaForge will give you access to everything you need to install OpenFF software. If you can, we recommend installing MambaForge locally to your user account, rather than system-wide, so that you can freely create and destroy environments and manage your own configuration. If something goes wrong, you can always delete your MambaForge installation and start again, and you'll only lose your installed software.

Mamba can be installed to your own user account without root/sudo access. A system-wide multi-user Conda/Mamba installation is [complicated] and generally not necessary.

:::{hint}
If you're running Mamba through MambaForge, you're configured to use the Conda Forge channel by default, and you don't need to pass the `-c conda-forge` argument to the commands in this page. Including this argument does no harm, so we've included it for the benefit of users that don't have this configuration.
:::

[complicated]: inv:conda#user-guide/configuration/admin-multi-user-install

(conda_init)=
### To init or not to init

After it's done installing, the MambaForge installer will ask you if you want it to initialize MambaForge. Initialization involves adding a section to your shell startup script that tells the shell where to find Conda/Mamba. Answering "no" will leave you startup scripts untouched, but you will need to run an additional command every time you want to use Conda/Mamba or a Conda environment. Answering "yes" will attempt to add a version of this command to your shell startup script, which generally makes Conda easier to use.

If you do answer "yes", we recommend preventing Conda from activating the base environment in every new shell:

```shell-session
$ conda config --set auto_activate_base false
```

This will prevent any conflicts between the MambaForge Python installation and the Python expected by your system. It does not prevent you from using Conda/Mamba directly to manage or activate environments.

(existing_conda)=
### Installing Mamba in an existing Conda installation

If you already have Conda installed, you don't need to install MambaForge; you can install Mamba on its own into the base environment with:

```shell-session
$ conda install -n base -c conda-forge mamba
```

Or you can simply replace any calls to `mamba` with an identical call to `conda`:

```diff
- mamba env create -c conda-forge -n openff -f environment.yaml
+ conda env create -c conda-forge -n openff -f environment.yaml
```

We recommend installing Mamba, as it can solve OpenFF environments in seconds where Conda would take minutes or hours.

Conda environments that use packages from Conda Forge alongside packages from the default Conda channels run the risk of breaking when an installation or update is attempted. This most commonly happens when a user forgets the `-c conda-forge` switch when installing a package or updating an environment (see [](combining_channels)). If you are using a standard Conda installation, we recommend configuring environments with Forge dependencies to use Forge wherever possible:

```shell-session
$ conda activate openff
$ conda config --env --add channels conda-forge
$ conda config --env --set channel_priority strict 
```

In environments with this configuration, the `-c conda-forge` switch is unnecessary. Other channels, like `psi4` and `bioconda`, can still be used in the usual way. These settings can be applied to all your Conda environments by removing the `--env` switches, matching the default MambaForge configuration.

(managing_environments)=
## Managing Environments

Conda and Mamba install software into [virtual environments]. These environments include installations of some collection of software and all their dependencies in an isolated group that doesn't affect the software installed in the rest of your computer system. This means you can install software that's incompatible with what's already installed; you just put the new software in its own environment!

Virtual environments are designed to be rapidly deployable, which also means they can quickly and safely be removed and re-created in a matter of seconds when something goes wrong. Recreating an environment with just the packages you need is usually easier than troubleshooting an existing one, and often its even preferable to updating or installing new software in one! If you run into any problems at all with an existing environment, try just creating a new one with all the packages you want to use.

Distributions of Conda/Mamba come with a **base environment**, which includes the installation of the package manager itself. We highly recommend leaving this environment alone! If you make a mistake and install software from a conflicting channel, or say "install anyway" one too many times, or sneeze while staring at your shadow at noon on midsummer's eve during an update, you could break your entire Conda/Mamba install. All of us at OpenFF have done this at least once! It's not the end of the world, since hopefully that Conda/Mamba install was [local to your user] and you can just delete it and reinstall, but it is frustrating.

Instead of installing software into your base environment, we recommend creating new environments to install software into as you go. Some people prefer to have one big environment they install everything into, while others prefer a few smaller ones that each have the software needed for a particular task. Some of us even spin up a new environment every time they start a PR!

A new environment can be created from a list of packages:

```shell-session
$ mamba create -n <environment name> -c conda-forge <package(s)>
```

Or from an [environment file], which can specify both channels and dependencies:

```shell-session
$ mamba env create -n <name> -f <path to .yaml file>
```

Any time you want to use software installed in an environment you have created, you must activate it. An environment will stay active until you close the terminal window or shell session:

```shell-session
$ conda activate <name>
$ jupyter-lab .
```

[virtual environments]: inv:conda#user-guide/concepts/environments
[local to your user]: install_mamba

### Advanced Environment Management

Mamba/Conda cache the packages you install, so if you've already downloaded a particular version, you can install it in as many environments as you like without having to re-download it. In fact, Mamba/Conda try their hardest to unpack each version once, and then hardlink to it from each environment to keep the storage size of environments down. So don't be afraid to just create a new environment! 

Because of this linking behavior, package code is often shared among different environments. If you edit one environment's `lib/python/site-packages` directory for example, those changes are likely to affect other environments. If you want to tinker with the code of your dependencies, consider using the `--copy` argument when installing them to avoid linking!

If you prefer, you can specify the path to a virtual environment's root directory as a prefix instead of giving an environment's name. This can be useful for temporary environments, or for environments that are local to a project:

```shell-session
$ mamba create -c conda-forge -p <prefix> <package(s)>
$ conda activate <prefix>
```

If you specify neither the name `-n` nor the prefix `-p`, the current active environment will be used.

New software can be installed in an environment by listing packages:

```shell-session
$ mamba install -n <name> -c conda-forge <package(s)>
```

Or by adding the dependencies from an environment file:

```shell-session
$ mamba env update -n <name> -f <path to .yaml file>
```

The software in an environment can be automatically upgraded:

```shell-session
$ mamba upgrade -n <name> --all
```

But that can go wrong if you're mixing channels and might be slow if the environment is old. Recreating the environment often works better:

```shell-session
$ mamba env remove -n <name>
$ mamba create -n <name> -c conda-forge <package(s)>
```

Or specifying the particular package you want to update:

```shell-session
$ mamba upgrade -n <name> <package>
```

(combining_channels)=
### Combining channels

Sometimes, some of the software you want to use is not available on Conda Forge. In these cases, you can either install it in the usual way for your OS, or you can try combining channels:

```shell-session
$ mamba create -n psi4_and_bespokefit -c psi4 -c conda-forge -c anaconda openff-bespokefit psi4
```

In this case, this doesn't work because Conda/Mamba has to be very clever about how it solves this environment. It has to be able to choose versions of dependencies from the `anaconda` channel, even when those dependencies exist in the higher-priority `conda-forge` channel. We can't make `anaconda` the higher priority channel, because BespokeFit needs Forge dependencies. It's generally recommended to use [strict channel priority] to avoid conflicts, but sometimes an environment can only be solved when channel priority is set to `"flexible"`. The catch is that the environment may solve and install but not work! But it's usually worth a try.

This environment is also complex enough that remembering all the channels every time you want to update it is risky. So instead of trying to create it in one line, we might be better off creating it empty, configuring its channel list and priorities, and then installing our software:

```shell-session
$ mamba create -n psi4_and_bespokefit
$ conda activate psi4_and_bespokefit
$ conda config --env --set channel_priority flexible
$ conda config --env --prepend channels anaconda
$ conda config --env --prepend channels conda-forge
$ conda config --env --prepend channels psi4
$ mamba install openff-bespokefit psi4 ambertools
```

[environment file]: inv:conda#create-env-file-manually
[strict channel priority]: inv:conda#concepts-performance-channel-priority

(install_windows)=
## OpenFF on Windows

OpenFF does not support or test on Windows natively. All of our software is pure Python code and may work anyway as long as you can provide our dependencies, but many of these dependencies are not available on Windows and may not be in the foreseeable future.

Instead, we recommend using the [Windows Subsystem for Linux] to run OpenFF software on Windows. WSL runs a Linux kernel within your Windows system so you can run ordinary software as if you had a Linux system. If your hardware supports it, we suggest using WSL2 for a smoother experience; this is the default for new WSL installations on supported hardware. WSL2 requires hardware virtualization support, which is available on most modern CPUs but may require activation in the BIOS/UEFI. 

In either case, once WSL is installed you can usually follow any documentation as though you had a Linux machine.

Note that by default, Jupyter Notebook may not be able to open a browser window, and so may log an error on startup; just ignore the error and open the link it provides in your ordinary Windows web browser.

:::{hint}
WSL2 [does support](https://developer.nvidia.com/cuda/wsl) GPU compute, at least with NVIDIA cards, but setting it up [takes some work](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute).
:::

[Windows Subsystem for Linux]: https://learn.microsoft.com/en-us/windows/wsl/about

(install_arm)=
## OpenFF on Apple Silicon and ARM

As of January 2024, OpenFF software and most of its corner of the computational chemistry ecosystem (OpenMM, RDKit, Psi4, etc.) support Apple Silicon (M1, M2, etc.). However, this may not be true if, for example, using old versions of any software. In such cases, we recommend macOS users of Apple Silicon install the x86_64 version of MambaForge and run all OpenFF software through [Rosetta]. ARM systems without access to a similar emulation layer may not be able to access all of the features of OpenFF software.

An existing ARM installation of Conda can be configured to [use Rosetta] with the `CONDA_SUBDIR=osx-64` shell environment variable or the `subdir` Conda config variable. We recommend using this on a per-environment basis so that it persists across updates and new installs, but does not affect existing setups:

```shell-session
$ CONDA_SUBDIR=osx-64 conda create --name openff -c conda-forge openff-toolkit
$ conda activate
$ conda config --env --set subdir osx-64
```

Alternatively, make this setting the global default by updating the system Conda config:

```shell-session
$ conda config --system --set subdir osx-64
```

Note that this will affect how Conda behaves with other environments.

[Rosetta]: https://support.apple.com/en-au/HT211861
[use Rosetta]: https://conda-forge.org/docs/user/tipsandtricks/#installing-apple-intel-packages-on-apple-silicon
