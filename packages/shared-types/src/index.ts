export * from './products';
export * from './orders';
export * from './users';
export * from './api';

// Export full generated OpenAPI spec contracts
export * from './openapi';

// Re-export Schemas from OpenAPI Contract
import type { components, paths } from './openapi';

export type Schemas = components['schemas'];

// 1. Sistema, Errores y Tipos Base
export type NonNegativeDecimalString = Schemas['NonNegativeDecimalString'];
export type ProblemDetails = Schemas['ProblemDetails'];
export type ErrorResponse = ProblemDetails;
export type PaginationMeta = Schemas['PaginationMeta'];
export type HealthResponse = Schemas['HealthResponse'];

// 2. Finanzas y Contabilidad
export type Account = Schemas['Account'];
export type AccountCreateInput = Schemas['AccountCreateInput'];
export type PaginatedAccounts = Schemas['PaginatedAccounts'];
export type JournalItem = Schemas['JournalItem'];
export type JournalItemInput = Schemas['JournalItemInput'];
export type JournalEntry = Schemas['JournalEntry'];
export type JournalEntryCreateInput = Schemas['JournalEntryCreateInput'];
export type PaginatedJournalEntries = Schemas['PaginatedJournalEntries'];

// 3. Tributario / DTE
export type DTE = Schemas['DTE'];
export type DTECreateInput = Schemas['DTECreateInput'];
export type PaginatedDtes = Schemas['PaginatedDtes'];

// 4. Egresos con Insumos
export type Expense = Schemas['Expense'];
export type ExpenseCreateInput = Schemas['ExpenseCreateInput'];
export type ExpenseRejectInput = Schemas['ExpenseRejectInput'];
export type ExpenseItemDetail = Schemas['ExpenseItemDetail'];
export type ExpenseItemDetailInput = Schemas['ExpenseItemDetailInput'];
export type PaginatedExpenses = Schemas['PaginatedExpenses'];

// 5. Bóveda de Documentos
export type DocumentMetadata = Schemas['DocumentMetadata'];

// 6. Flujo de Producción y Costeo
export type Ingredient = Schemas['Ingredient'];
export type IngredientCreateInput = Schemas['IngredientCreateInput'];
export type PaginatedIngredients = Schemas['PaginatedIngredients'];
export type RecipeIngredientItem = Schemas['RecipeIngredientItem'];
export type RecipeIngredientItemInput = Schemas['RecipeIngredientItemInput'];
export type RecipePackagingItem = Schemas['RecipePackagingItem'];
export type Recipe = Schemas['Recipe'];
export type RecipeCreateInput = Schemas['RecipeCreateInput'];
export type PaginatedRecipes = Schemas['PaginatedRecipes'];
export type ProductCostingAnalysis = Schemas['ProductCostingAnalysis'];
export type ProductionOrder = Schemas['ProductionOrder'];
export type ProductionOrderCreateInput = Schemas['ProductionOrderCreateInput'];
export type PaginatedProductionOrders = Schemas['PaginatedProductionOrders'];

export type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'options' | 'head' | 'patch' | 'trace';
