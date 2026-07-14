export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <main style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h1>🧪 Test de deploy — funciona</h1>
      <p>Generado en: {new Date().toISOString()}</p>
    </main>
  );
}
