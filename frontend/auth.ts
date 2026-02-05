import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"

export const { handlers, signIn, signOut, auth } = NextAuth({
  debug: true,
  trustHost: true,
  providers: [
    Credentials({
      credentials: {
        password: { label: "Password", type: "password" },
      },
      authorize: async (credentials) => {
        // Simulating a database check
        // In the future, you check this against your real DB
        if (credentials.password === "admin123") {
          return { id: "1", name: "Admin User", email: "admin@dpdp.com" }
        }
        return null
      },
    }),
  ],
  pages: {
    signIn: "/login", // We will build this custom page next
  },
})