import { useEffect, useState } from "react";
import { Box, Group, Stack, Text, Title } from "@mantine/core";
import { colors, fonts } from "./theme";
import { fetchHealth } from "./api";

type Status = "carregando" | "no ar" | "indisponível" | "sem resposta";

function StatusRow({ label, status }: { label: string; status: Status }) {
  const color =
    status === "no ar" ? colors.positive : status === "carregando" ? colors.inkMuted : colors.negative;
  return (
    <Group justify="space-between" py="sm" style={{ borderTop: `1px solid ${colors.line}` }}>
      <Text c={colors.inkMuted}>{label}</Text>
      <Text c={color} fw={600}>
        {status}
      </Text>
    </Group>
  );
}

export default function SystemStatus() {
  const [api, setApi] = useState<Status>("carregando");
  const [database, setDatabase] = useState<Status>("carregando");

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((health) => {
        if (!active) return;
        // The API answered, so it is up even when something inside it is down.
        setApi("no ar");
        setDatabase(health.components?.db?.status === "UP" ? "no ar" : "indisponível");
      })
      .catch(() => {
        if (!active) return;
        setApi("indisponível");
        setDatabase("sem resposta");
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <Box bg={colors.surfaceBase} c={colors.ink} mih="100dvh">
      <Box maw={430} mx="auto" px="lg" pt={48}>
        <Text
          component="span"
          style={{ fontSize: 12, letterSpacing: "1.2px", textTransform: "uppercase" }}
          c={colors.inkMuted}
        >
          Personal finance
        </Text>
        <Title order={1} mt="xs" style={{ fontFamily: fonts.display, fontSize: 34 }}>
          Estado do sistema
        </Title>
        <Stack gap={0} mt="xl">
          <StatusRow label="API" status={api} />
          <StatusRow label="Banco de dados" status={database} />
        </Stack>
      </Box>
    </Box>
  );
}
