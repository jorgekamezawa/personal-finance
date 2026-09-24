import { useEffect, useState } from "react";
import { Box, Group, Stack, Text, Title } from "@mantine/core";
import { cores, fontes } from "./theme";
import { buscarSaude } from "./api";

type Estado = "carregando" | "no ar" | "indisponível";

function Linha({ nome, estado }: { nome: string; estado: Estado }) {
  const cor =
    estado === "no ar" ? cores.positive : estado === "carregando" ? cores.inkMuted : cores.negative;
  return (
    <Group justify="space-between" py="sm" style={{ borderTop: `1px solid ${cores.line}` }}>
      <Text c={cores.inkMuted}>{nome}</Text>
      <Text c={cor} fw={600}>
        {estado}
      </Text>
    </Group>
  );
}

export default function StatusDoSistema() {
  const [api, setApi] = useState<Estado>("carregando");
  const [banco, setBanco] = useState<Estado>("carregando");

  useEffect(() => {
    let ativo = true;
    buscarSaude()
      .then((saude) => {
        if (!ativo) return;
        setApi(saude.status === "UP" ? "no ar" : "indisponível");
        setBanco(saude.components?.db?.status === "UP" ? "no ar" : "indisponível");
      })
      .catch(() => {
        if (!ativo) return;
        setApi("indisponível");
        setBanco("indisponível");
      });
    return () => {
      ativo = false;
    };
  }, []);

  return (
    <Box bg={cores.surfaceBase} c={cores.ink} mih="100dvh">
      <Box maw={430} mx="auto" px="lg" pt={48}>
        <Text
          component="span"
          style={{ fontSize: 12, letterSpacing: "1.2px", textTransform: "uppercase" }}
          c={cores.inkMuted}
        >
          Personal finance
        </Text>
        <Title order={1} mt="xs" style={{ fontFamily: fontes.display, fontSize: 34 }}>
          Estado do sistema
        </Title>
        <Stack gap={0} mt="xl">
          <Linha nome="API" estado={api} />
          <Linha nome="Banco de dados" estado={banco} />
        </Stack>
      </Box>
    </Box>
  );
}
