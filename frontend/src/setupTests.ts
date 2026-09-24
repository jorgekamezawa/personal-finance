import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// O Mantine consulta preferências do sistema; o ambiente de teste não tem essa API.
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
