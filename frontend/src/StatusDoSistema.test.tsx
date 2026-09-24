import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { afterEach, describe, expect, it, vi } from "vitest";
import StatusDoSistema from "./StatusDoSistema";
import { theme } from "./theme";

function renderizar() {
  return render(
    <MantineProvider theme={theme} forceColorScheme="dark">
      <StatusDoSistema />
    </MantineProvider>,
  );
}

function respondeCom(corpo: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({ ok, status: ok ? 200 : 503, json: async () => corpo })),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("tela de estado do sistema", () => {
  it("mostra API e banco no ar quando o backend responde", async () => {
    respondeCom({ status: "UP", components: { db: { status: "UP" } } });

    renderizar();

    expect(await screen.findAllByText("no ar")).toHaveLength(2);
  });

  it("mostra banco indisponível quando só o banco está fora", async () => {
    respondeCom({ status: "DOWN", components: { db: { status: "DOWN" } } });

    renderizar();

    expect(await screen.findAllByText("indisponível")).toHaveLength(2);
  });

  it("mostra tudo indisponível quando a API não responde", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("sem rede");
      }),
    );

    renderizar();

    expect(await screen.findAllByText("indisponível")).toHaveLength(2);
  });
});
