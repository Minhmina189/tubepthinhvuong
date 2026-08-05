import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        coral: {
          50: "#fff1f0",
          100: "#ffe1de",
          400: "#f07a70",
          500: "#e8635a",
          600: "#d44d44",
        },
        cream: "#FAF8F5",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
