# flake.nix
# Installs golang and gopls, python 3.12, and bun
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = system: import nixpkgs { system = system; };
    in
    {
      devShells = builtins.mapAttrs (system: pkgs: {
          default = pkgs.mkShell {
            name = "dev-environment";
            packages = with pkgs; [
              go
              gopls
              (python312.withPackages (ps: [
                ps.ruff
                ps.uv
                ps.flask
                ps.flask-cors
                ps.requests
              ]))
              bun
            ];

            shellHook = ''
                echo ${pkgs.go} ${pkgs.gopls}
                echo ${pkgs.uv}
                echo ${pkgs.bun}
            '';
          };
        }) {
          "x86_64-darwin" = pkgs "x86_64-darwin";
          "aarch64-darwin" = pkgs "aarch64-darwin";
        };
    };
}
