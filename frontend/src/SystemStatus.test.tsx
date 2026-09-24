import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { afterEach, describe, expect, it, vi } from "vitest";
import SystemStatus from "./SystemStatus";
import { theme } from "./theme";

function renderScreen() {
  return render(
    <MantineProvider theme={theme} forceColorScheme="dark">
      <SystemStatus />
    </MantineProvider>,
  );
}

function apiAnswers(body: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({ ok, status: ok ? 200 : 503, json: async () => body })),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("system status screen", () => {
  it("shows api and database up when the backend answers", async () => {
    apiAnswers({ status: "UP", components: { db: { status: "UP" } } });

    renderScreen();

    expect(await screen.findAllByText("no ar")).toHaveLength(2);
  });

  it("shows the api up and the database down when only the database is out", async () => {
    apiAnswers({ status: "DOWN", components: { db: { status: "DOWN" } } }, false);

    renderScreen();

    expect(await screen.findByText("indisponível")).toBeInTheDocument();
    expect(screen.getByText("no ar")).toBeInTheDocument();
  });

  it("shows the api down and no answer for the database when the api fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("no network");
      }),
    );

    renderScreen();

    expect(await screen.findByText("indisponível")).toBeInTheDocument();
    expect(screen.getByText("sem resposta")).toBeInTheDocument();
  });
});
