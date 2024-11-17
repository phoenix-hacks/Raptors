module.exports = {
  async headers() {
      return [
          {
              // Allow CORS for all API routes
              source: "/api/:path*",
              headers: [
                  { key: "Access-Control-Allow-Credentials", value: "true" },
                  { key: "Access-Control-Allow-Origin", value: "http://localhost:5000" }, // Your backend URL
                  { key: "Access-Control-Allow-Methods", value: "GET,POST,OPTIONS" },
                  { key: "Access-Control-Allow-Headers", value: "Content-Type, Authorization" },
              ]
          }
      ]
  },
}