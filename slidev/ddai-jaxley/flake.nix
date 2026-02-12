{
  description = "Jaxley DDAI Presentation Env";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [go-task bun cloudflared];
        shellHook = ''
          echo ${pkgs.go-task}
          echo ${pkgs.bun}
          echo ${pkgs.cloudflared}
        '';
      };
    });
}
