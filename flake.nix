{
  description = "TODO description";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, ... } @ inputs:
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = inputs.nixpkgs.legacyPackages."${system}";
        pythonPackages = pkgs.python311Packages;

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
          src = pkgs.fetchFromGitea {
            domain = "gitea.arianb.me";
            owner = "arian";
            repo = "tibasic-script";
            rev = "c7563f1b8a89003dea6983dc67b5c80f981c1d7e";
            hash = "sha256-n9solnaAQrteGNk5jg8WdbU+Um4OZMH1/soQjupMr1k=";
          };
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
