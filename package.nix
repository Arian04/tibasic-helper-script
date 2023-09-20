{ lib
, python311Packages
, fetchPypi
, fetchFromGitea
}:

let
  tivars = python311Packages.buildPythonPackage rec {
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
python311Packages.buildPythonPackage rec {
  name = "tibasic-compile";
  src = fetchFromGitea {
    domain = "gitea.arianb.me";
    owner = "arian";
    repo = "tibasic-script";
    rev = "5b494fa9a4b21846b8b5e1f63b0c3a414762346a";
    hash = "sha256-MryuKuGXQe6xlKSWBhuHZyRwDGS8xjoKvHCuJh8MWYc=";
  };
  propagatedBuildInputs = [
    tivars
  ];

  doCheck = false;

  meta = {
  homepage = "https://gitea.arianb.me/arian/tibasic-script";
  maintainers = [ ];
  };
}
