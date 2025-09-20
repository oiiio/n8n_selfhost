module.exports = {
	preset: 'ts-jest',
	testEnvironment: 'node',
	roots: ['<rootDir>/nodes'],
	testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
	transform: {
		'^.+\\.ts$': 'ts-jest',
	},
	collectCoverageFrom: [
		'nodes/**/*.ts',
		'!nodes/**/*.d.ts',
	],
};