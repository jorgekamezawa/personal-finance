export type Saude = {
  status: string;
  components?: Record<string, { status: string }>;
};

/** Pergunta ao backend, na mesma origem, como ele e o banco estão (ADR-0016). */
export async function buscarSaude(): Promise<Saude> {
  const resposta = await fetch("/api/health");
  if (!resposta.ok) {
    throw new Error(`resposta ${resposta.status}`);
  }
  return (await resposta.json()) as Saude;
}
