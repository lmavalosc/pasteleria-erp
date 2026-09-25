export * from './products';
export * from './orders';
export * from './users';
export * from './api';

// Export full generated OpenAPI spec contracts
export * from './openapi';

// Re-export Schemas from OpenAPI Contract
import type { components, paths } from './openapi';

export type Schemas = components['schemas'];

// 1. Sistema
export type HealthResponse = Schemas['HealthResponse'];
export type ErrorResponse = Schemas['ErrorResponse'];

// 2. Finanzas y Contabilidad
export type Account = Schemas['Account'];
export type AccountCreateInput = Schemas['AccountCreateInput'];
export type JournalItem = Schemas['JournalItem'];
export type JournalItemInput = Schemas['JournalItemInput'];
export type JournalEntry = Schemas['JournalEntry'];
export type JournalEntryCreateInput = Schemas['JournalEntryCreateInput'];

// 3. Tributario / DTE
export type DTE = Schemas['DTE'];
export type DTECreateInput = Schemas['DTECreateInput'];

// 4. Egresos con Insumos
export type Expense = Schemas['Expense'];
export type ExpenseCreateInput = Schemas['ExpenseCreateInput'];
export type ExpenseRejectInput = Schemas['ExpenseRejectInput'];
export type ExpenseItemDetail = Schemas['ExpenseItemDetail'];
export type ExpenseItemDetailInput = Schemas['ExpenseItemDetailInput'];

// 5. Bóveda de Documentos
export type DocumentMetadata = Schemas['DocumentMetadata'];

// 6. Flujo de Producción y Costeo
export type Ingredient = Schemas['Ingredient'];
export type IngredientCreateInput = Schemas['IngredientCreateInput'];
export type RecipeIngredientItem = Schemas['RecipeIngredientItem'];
export type RecipeIngredientItemInput = Schemas['RecipeIngredientItemInput'];
export type RecipePackagingItem = Schemas['RecipePackagingItem'];
export type Recipe = Schemas['Recipe'];
export type RecipeCreateInput = Schemas['RecipeCreateInput'];
export type ProductCostingAnalysis = Schemas['ProductCostingAnalysis'];
export type ProductionOrder = Schemas['ProductionOrder'];
export type ProductionOrderCreateInput = Schemas['ProductionOrderCreateInput'];

export type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'options' | 'head' | 'patch' | 'trace';
