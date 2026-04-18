const nextJest = require("next/jest");

const createJestConfig = nextJest({ dir: "./" });

/** @type {import('jest').Config} */
const config = {
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  testMatch: ["**/__tests__/**/*.test.{ts,tsx}"],
  collectCoverageFrom: [
    "components/**/*.{ts,tsx}",
    "lib/auth/**/*.{ts,tsx}",
    "app/login/**/*.{ts,tsx}",
    "app/register/**/*.{ts,tsx}",
    "!**/*.d.ts",
    "!components/session/InterviewSessionClient.tsx",
    "!components/session/SessionSetupClient.tsx",
  ],
};

module.exports = createJestConfig(config);
