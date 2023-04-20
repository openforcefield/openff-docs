# Open Force Field Software

Welcome to the documentation for the [Open Force Field Initiative]'s software ecosystem.

[Open Force Field Initiative]: https://openforcefield.org

## Getting Started

Instructions for installing and using OpenFF software can be found at [](install) and in the project-specific documentation below. If you want to understand how to use OpenFF force fields, or if you want to see what's possible, see [](modelling).

## Standards

Specifications for SMIRNOFF and other standards defined by OpenFF can be found at [OpenFF Standards](https://docs.openforcefield.org/standards).

(projects)=
## Projects

[`openff-toolkit`](https://docs.openforcefield.org/projects/toolkit)
: Tools for preparing systems and manipulating force fields

[`openff-interchange`](https://docs.openforcefield.org/projects/interchange)
: Parametrize and export systems ready for simulation to various MD engines

[`openff-units`](https://docs.openforcefield.org/projects/units)
: Unified units of measure handling for the OpenFF ecosystem based on Pint

[`openff-bespokefit`](https://docs.openforcefield.org/projects/bespokefit)
: Automated parameter optimization for specific molecules or series of molecules

[`openff-qcsubmit`](https://docs.openforcefield.org/projects/qcsubmit)
: Submit and retrieve datasets with rich metadata from QCFractal instances

[`openff-fragmenter`](https://docs.openforcefield.org/projects/fragmenter)
: Fragment molecules for efficient quantum mechanical torsion scans 

[`openff-evaluator`](https://docs.openforcefield.org/projects/evaluator)
: Scalably and automatically estimate physical properties

[`openff-recharge`](https://docs.openforcefield.org/projects/recharge)
: Generate optimized partial charges for molecules with a variety of methods

[`openff-nagl`](https://docs.openforcefield.org/projects/nagl)
: Train and use machine-learned partial charge models targetting molecular graphs

## Contact Us

Need help? Raise an issue on [GitHub], open a topic on our [Discourse forum], or [email us]!

[GitHub]: https://github.com/openforcefield
[Discourse forum]: https://discourse.openforcefield.org/
[email us]: mailto:support@openforcefield.org

:::{toctree}
---
hidden: True
maxdepth: 1
---

Overview <self>
OpenFF Standards <https://docs.openforcefield.org/standards>
:::

:::{toctree}
---
hidden: True
maxdepth: 1
caption: Getting Started
---

install
modelling
:::

:::{toctree}
---
hidden: True
maxdepth: 1
caption: Projects
---

OpenFF Toolkit <https://docs.openforcefield.org/projects/toolkit>
Interchange <https://docs.openforcefield.org/projects/interchange>
Units <https://docs.openforcefield.org/projects/units>
BespokeFit <https://docs.openforcefield.org/projects/bespokefit>
QCSubmit <https://docs.openforcefield.org/projects/qcsubmit>
Fragmenter <https://docs.openforcefield.org/projects/fragmenter>
Evaluator <https://docs.openforcefield.org/projects/evaluator>
Recharge <https://docs.openforcefield.org/projects/recharge>
NAGL <https://docs.openforcefield.org/projects/nagl>
:::
