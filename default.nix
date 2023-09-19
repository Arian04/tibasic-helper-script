let
  pkgs = import <nixpkgs> {};
  build = pkgs.python311Packages.callPackage ./package.nix {};
in {
  inherit build;
  shell = pkgs.mkShell {
    inputsFrom = [ build ];
    packages = with pkgs.python311Packages; [
      black
      virtualenvwrapper
    ];
  };
}
