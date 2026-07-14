import { supabase } from "@/lib/supabase";

export default async function Home() {
  const { count: cantProductos, error: errorProductos } = await supabase
    .from("productos")
    .select("*", { count: "exact", head: true });

  const { data: config, error: errorConfig } = await supabase
    .from("config")
    .select("*")
    .single();

  const hayError = errorProductos || errorConfig;

  return (
    <main className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-negocio-primario mb-2">
        StockMaster Pro
      </h1>
      <p className="text-gray-500 mb-8">Versión web — en migración 🚧</p>

      <div className="bg-white rounded-lg shadow p-6 space-y-3">
        <h2 className="font-semibold text-lg">Estado de conexión a Supabase</h2>

        {hayError ? (
          <div className="text-red-600">
            <p>❌ Hubo un problema conectando con Supabase.</p>
            <pre className="text-xs bg-red-50 p-3 rounded mt-2 overflow-auto">
              {JSON.stringify(errorProductos || errorConfig, null, 2)}
            </pre>
            <p className="text-sm mt-2 text-gray-600">
              Revisá que hayas corrido <code>schema.sql</code> en Supabase y
              que las variables de entorno en <code>.env.local</code> sean
              correctas.
            </p>
          </div>
        ) : (
          <div className="text-green-700 space-y-1">
            <p>✅ Conectado correctamente</p>
            <p>
              Negocio configurado:{" "}
              <strong>{config?.nombre_negocio ?? "(sin nombre)"}</strong>
            </p>
            <p>
              Productos cargados: <strong>{cantProductos ?? 0}</strong>
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
