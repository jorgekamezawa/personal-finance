import { createTheme, rem } from "@mantine/core";

/**
 * Valores vindos do Sistema visual (ver .claude/rules/frontend.md).
 * Mudança visual nasce lá e é aplicada aqui; nunca o contrário, e nunca direto na tela.
 */
export const cores = {
  surfaceBase: "#191b1a",
  surfaceRaised: "#1f2220",
  line: "#2d302e",
  ink: "#ecefe9",
  inkMuted: "#8d938a",
  accent: "#c7e0c0",
  accentInk: "#1b231a",
  positive: "#a8d8a0",
  negative: "#e5a08c",
  warning: "#e3c178",
} as const;

export const fontes = {
  display: "Fraunces, Georgia, serif",
  sans: '"Plus Jakarta Sans", system-ui, sans-serif',
} as const;

export const theme = createTheme({
  fontFamily: fontes.sans,
  headings: { fontFamily: fontes.display, fontWeight: "600" },
  defaultRadius: "md",
  radius: { sm: rem(8), md: rem(10), lg: rem(16) },
  spacing: {
    xs: rem(4),
    sm: rem(8),
    md: rem(16),
    lg: rem(24),
    xl: rem(32),
  },
  colors: {
    sage: [
      "#f2f8f0",
      "#e4f0e0",
      "#d6e8d0",
      "#c7e0c0",
      "#b3d2ab",
      "#9fc496",
      "#8ab681",
      "#76a86c",
      "#5f8f57",
      "#487642",
    ],
  },
  primaryColor: "sage",
  primaryShade: 3,
});
