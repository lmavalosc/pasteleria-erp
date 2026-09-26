export * from './products';
export * from './orders';
export * from './users';
export * from './api';

// Export full generated OpenAPI spec contracts
export * from './openapi';

// Re-export Schemas from OpenAPI Contract
import type { components, paths } from './openapi';

export type Schemas = components['schemas'];

// 1. Tipos Base y Errores
export type Uuid = Schemas['Uuid'];
export type DateString = Schemas['Date'];
export type DateTimeString = Schemas['DateTime'];
export type DecimalString = Schemas['DecimalString'];
export type NonNegativeDecimalString = Schemas['NonNegativeDecimalString'];
export type ProblemDetail = Schemas['ProblemDetail'];
export type ProblemDetails = Schemas['ProblemDetail'];
export type ErrorDetail = Schemas['ErrorDetail'];
export type PageMeta = Schemas['PageMeta'];
export type Currency = Schemas['Currency'];

// 2. Sistema
export type HealthResponse = Schemas['HealthResponse'];

// 3. Contabilidad
export type AccountType = Schemas['AccountType'];
export type AccountingAccount = Schemas['AccountingAccount'];
export type AccountingAccountCreate = Schemas['AccountingAccountCreate'];
export type AccountingAccountUpdate = Schemas['AccountingAccountUpdate'];
export type AccountingAccountPage = Schemas['AccountingAccountPage'];

export type JournalStatus = Schemas['JournalStatus'];
export type JournalLine = Schemas['JournalLine'];
export type JournalLineCreate = Schemas['JournalLineCreate'];
export type JournalEntry = Schemas['JournalEntry'];
export type JournalEntryCreate = Schemas['JournalEntryCreate'];
export type JournalEntryPage = Schemas['JournalEntryPage'];

// 4. Facturación / DTE
export type DteType = Schemas['DteType'];
export type DteStatus = Schemas['DteStatus'];
export type DteInvoice = Schemas['DteInvoice'];
export type DteInvoiceCreate = Schemas['DteInvoiceCreate'];
export type DteInvoicePage = Schemas['DteInvoicePage'];

// 5. Gastos
export type ExpenseStatus = Schemas['ExpenseStatus'];
export type Expense = Schemas['Expense'];
export type ExpenseCreate = Schemas['ExpenseCreate'];
export type ExpenseUpdate = Schemas['ExpenseUpdate'];
export type ExpensePage = Schemas['ExpensePage'];

// 6. Documentos
export type Document = Schemas['Document'];
export type DocumentUploadRequest = Schemas['DocumentUploadRequest'];
export type DocumentPage = Schemas['DocumentPage'];

// Compatibilidad
export type Account = AccountingAccount;
export type AccountCreateInput = AccountingAccountCreate;
export type JournalItem = JournalLine;
export type JournalItemInput = JournalLineCreate;
export type JournalEntryCreateInput = JournalEntryCreate;
export type DTE = DteInvoice;
export type DTECreateInput = DteInvoiceCreate;
export type ExpenseCreateInput = ExpenseCreate;
export type DocumentMetadata = Document;

export type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'options' | 'head' | 'patch' | 'trace';
