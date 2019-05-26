# Change Log

## v0.1.6dev
 - Add documentation on [Read The Docs](https://femethods.readthedocs.io/en/latest/index.html)
 - Expand module and function documentation
 - Rename module from FEMethods to FEmethods (lower case m)

### Backwards Incompatible Changes
 - `Beam.plot` now returns a tuple to give access to the axes directly instead of just the figure
 - `Beam.plot` defaults changed to not automatically plot the beam stress

## v0.1.5dev
 - Add CI, coverage reports and expand unit tests
 - Rewrite existing tests using pytest
 - Invalidate `reactions` when when `elements.Beam` is invalidated
 - Add warnings when differentiating near beam ends
 - Add show method to wrap `matplotlib.pyplot.show` function

### Backwards Incompatible Changes
 - Renamed force parameter for `loads` from value to magnitude to avoid naming conflict

## v0.1.4dev
 - Adding unit tests to validate results for multiple cases
 - Formatting improvements
 - Added additional parameters
 - Re-factored loads and reaction properties
 - Fixed issue where reaction would not calculate properly when force was
   located directly over a reaction
