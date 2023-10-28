{
  description = "tibasic helper script thingy";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, ... } @ inputs:
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = inputs.nixpkgs.legacyPackages."${system}";
        pythonPackages = pkgs.python311Packages;

        # Having to maintain the version and hash in nix code instead of the lockfile doesn't seem
        # to be in line with nix flakes best practices but I need to figure out how I wanna move it
        # to the lockfile
        tivars = pythonPackages.buildPythonPackage rec {
          pname = "tivars";
          version = "0.8.0";
          format = "wheel";
          src = pkgs.fetchPypi {
            inherit pname version format;
            dist = "py3";
            python = "py3";
            #abi = "none";
            #platform = "any";
            sha256 = "sha256-bwdQG8JA4H2zd47i4Zt+wzoxzmT7ksGa/PbTajqKoHY=";
          };
        };
      in
      {
        packages.default = pythonPackages.buildPythonPackage {
          name = "tibasic-compile";
          src = ./.;
          propagatedBuildInputs = [
            tivars
          ];
          doCheck = false;
        };

        apps.default = {
          type = "app";
          program = "${self.packages."${system}".default}/bin/tibasic-compile";
        };

        devShells.default = with pkgs; mkShell {
          name = "dev-shell";
          buildInputs = [
            #self.packages."${system}".default.inputDerivation
            tivars
            pythonPackages.black
            nixpkgs-fmt
          ];
          shellHook = ''
            PATH=$PWD/src/tibasic_compile:$PATH
          '';
        };
      });
}
