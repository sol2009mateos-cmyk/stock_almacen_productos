# StockMaster Pro Web — Puesta en marcha (Paso 1)

## 1. Crear las tablas en Supabase

1. Entrá a tu proyecto: https://supabase.com/dashboard/project/bkssmlrfkwzhgxppijkg
2. Menú izquierdo > **SQL Editor** > **New query**
3. Pegá TODO el contenido de `supabase/schema.sql` y le das **Run**
4. (Opcional, recomendado para probar) Nueva query, pegás `supabase/seed_datos_prueba.sql` y **Run**
   - Esto carga 12 productos de prueba, para no arrancar con la pantalla vacía

## 2. Conseguir las credenciales de Supabase

1. En el dashboard de Supabase: **Project Settings** (ícono de engranaje) > **API**
2. Copiá:
   - **Project URL** → va en `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public key** → va en `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## 3. Configurar el proyecto localmente

```bash
# Descomprimís el zip que te pasé, entrás a la carpeta
cd stockmaster-web

# Copiás el archivo de ejemplo y completás con tus datos reales
cp .env.local.example .env.local
# Editá .env.local con tu URL y anon key de Supabase

# Instalás dependencias
npm install

# Levantás el proyecto en local
npm run dev
```

Abrí http://localhost:3000 — deberías ver la página de estado de conexión.
Si dice "✅ Conectado correctamente" y te muestra 12 productos, ¡vamos por buen camino!

## 4. Subir a tu GitHub

Vas a reemplazar el contenido del repo actual (que es la versión Tkinter) por este proyecto nuevo. Te recomiendo un repo nuevo o una rama nueva para no perder el código viejo:

```bash
git init
git add .
git commit -m "Setup inicial - migración a Next.js + Supabase"
git branch -M main
git remote add origin https://github.com/sol2009mateos-cmyk/stock_almacen_productos.git
git push -u origin main --force   # ojo si el repo ya tiene commits, avisame antes de hacer force
```

**Importante:** si el repo ya tiene el código viejo de Python y no querés perderlo, avisame antes de este paso y armamos una rama separada (ej. `migracion-web`) en lugar de pisar `main`.

## 5. Conectar con Vercel

1. Entrá a https://vercel.com/sol2009mateos-6990s-projects
2. **Add New > Project** > importás el repo de GitHub
3. En **Environment Variables** agregás las mismas 2 variables del `.env.local`:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. Deploy 🚀

---

Cuando tengas esto funcionando (local o ya en Vercel), avisame y seguimos con el **Paso 2: módulo de Inventario**.
