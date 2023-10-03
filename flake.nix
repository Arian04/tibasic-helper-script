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
            rev = "efb87ae460761c43c2e91deb3b2c78e472e00354";
            hash = "sha256-LV2oApkFNDXgkFc/IY4XHVKV/o5MQE6G/XM6nYKANYg=";
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
