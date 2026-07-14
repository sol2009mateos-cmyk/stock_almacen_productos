import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        negocio: {
          primario: "#0f766e",
          acento: "#f97316",
        },
      },
    },
  },
  plugins: [],
};
export default config;
