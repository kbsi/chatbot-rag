module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4da8ff',
          DEFAULT: '#0078ff',
          dark: '#0056cc',
        },
        chatbg: '#f7f7f8',
        usermessage: '#ffffff',
        botmessage: '#f0f4f9',
      },
    },
  },
  plugins: [],
}