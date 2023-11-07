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
- add flags to disable/enable each preprocessor feature
- add flags to disable/enable all preprocessor features at once
	- allows user to disable all, then enable one rather than having to disable all but one individually
	  and vice versa


- trim spaces after commas (in function or command param list)
	- ex: `Input "foo", F` -> `Input "foo",F`
	- since the latter runs while the former doesn't
- trim spaces around operators (+, -, ->, =, etc.)
- grab tokens from token list and create list of tokens that end in a space
	- after doing that, figure out if I should warn when encountering a token that
	  might've been intended to have a space after it or just fix it and add one
