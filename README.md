# TI-Basic script thing
I should add a description here or something

## Features
- uhhh cool ones
- neat ones
- awesome ones

## TODO
##### General
- migrate to pyproject.toml
- either package tilp2 (https://github.com/debrouxl/tilp_and_gfm/) for nix or get rid of my
  dependency on it by using one of the TIlibs libraries directly. Or since that's only a single
  feature of the script, I should detect which "install" methods are available at runtime? Or just
  fail in a "nicer" way if the binary isn't in PATH (ie: we fail with command not found error 127)

##### Preprocessor
- trim spaces after commas (that aren't in strings ofc)
	- ex: `Input "foo", F` -> `Input "foo",F`
	- since the latter runs while the former doesn't
