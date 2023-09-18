{ pkgs
, buildPythonPackage
, fetchPypi
, fetchFromGitea
,
}:

with pkgs;

let
  tivars = buildPythonPackage rec {
    pname = "tivars";
    version = "0.8.0";
    format = "wheel";
    src = fetchPypi {
      inherit pname version format;
      dist = "py3";
      python = "py3";
      #abi = "none";
      #platform = "any";
      sha256 = "sha256-bwdQG8JA4H2zd47i4Zt+wzoxzmT7ksGa/PbTajqKoHY=";
    };
  };
in
stdenv.mkDerivation {
  name = "tibasic-compile";
  src = fetchFromGitea {
    domain = "gitea.arianb.me";
    owner = "arian";
    repo = "tibasic-script";
    rev = "040a1100922a33c572fae35cc904aed51f31cb32";
    hash = "sha256-8J52fGohPFHXkbBOX1TGNX8vrFB+cHUcGDAiPc1zCEg=";
  };
  buildInputs = [
    tivars
  ];

  installPhase = ''
    install -Dm755 tibasic-compile.py $out/bin/tibasic-compile
  '';

  meta = {
    homepage = "https://gitea.arianb.me/arian/tibasic-script";
    description = "TODO desc";
    maintainers = with maintainers; [ arian ];
  };
}
