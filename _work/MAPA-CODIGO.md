# Mapa da Base de Código (FDD)

Análise estruturada do código-fonte para fundamentar os documentos de design, validada contra o `_work/CATALOGO.md`. Todos os arquivos citados abaixo foram abertos e inspecionados diretamente, com saídas cruas de `ls`, `grep -n` e `sed -n`, números de linha exatos e caminhos relativos à raiz do projeto.

---

## Parte A: Ganchos citados na reunião (Resumo com Provas)

| ID | O que a reunião disse / Gancho | Caminho encontrado | Linha(s) | Saída crua (`ls` / `grep -n` / `sed -n`) | Situação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T-56** | A transação atualiza `orders`, insere em `order_status_history` e decrementa `stock_quantity` | `src/modules/orders/order.service.ts` | 24, 126–179, 204–231 | `126:  async changeStatus(`<br>`131:    return this.prisma.$transaction(async (tx) => {`<br>`152:        await this.debitStock(tx, order.items);`<br>`158:      await tx.order.update({ where: { id }, data: { status: to } });`<br>`159:      await tx.orderStatusHistory.create({`<br>`178:    });`<br>`179:  }`<br>`228:        data: { stockQuantity: { decrement: item.quantity } },` | VERIFICADO |
| **T-57** | `AppError`, `InsufficientStockError` e `InvalidStatusTransitionError` com códigos e status HTTP | `src/shared/errors/app-error.ts`<br>`src/shared/errors/http-errors.ts` | `app-error.ts`: 3–16<br>`http-errors.ts`: 33–63 | `src/shared/errors/app-error.ts:3:export class AppError extends Error {`<br>`src/shared/errors/http-errors.ts:33:export class ConflictError extends AppError {`<br>`src/shared/errors/http-errors.ts:35:    super(message, 409, code, details);`<br>`src/shared/errors/http-errors.ts:39:export class UnprocessableEntityError extends AppError {`<br>`src/shared/errors/http-errors.ts:41:    super(message, 422, code, details);`<br>`src/shared/errors/http-errors.ts:45:export class InvalidStatusTransitionError extends ConflictError {`<br>`src/shared/errors/http-errors.ts:49:      'INVALID_STATUS_TRANSITION',`<br>`src/shared/errors/http-errors.ts:55:export class InsufficientStockError extends UnprocessableEntityError {`<br>`src/shared/errors/http-errors.ts:59:      'INSUFFICIENT_STOCK',` | VERIFICADO |
| **T-23** | Erros customizados `WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL`, etc. | `src/shared/errors/http-errors.ts` | — | `$ grep -n "WEBHOOK_" src/ -r`<br>`(no matches)` | NÃO EXISTE |
| **T-59** | Reaproveitar o `requireRole` existente (`ADMIN`) | `src/middlewares/auth.middleware.ts` | 6–10, 49–61 | `6:export type AuthUser = {`<br>`9:  role: 'ADMIN' \| 'OPERATOR';`<br>`49:export function requireRole(...roles: AuthUser['role'][]): RequestHandler {` | VERIFICADO |
| **T-24 (a)** | Middleware de erro centralizado trata `AppError`, `ZodError` e `Prisma.PrismaClientKnownRequestError` | `src/middlewares/error.middleware.ts` | 14–65 | `14:export const errorMiddleware: ErrorRequestHandler = (err, req, res, _next) => {`<br>`15:  if (err instanceof AppError) {`<br>`26:  if (err instanceof ZodError) {`<br>`37:  if (err instanceof Prisma.PrismaClientKnownRequestError) {` | VERIFICADO |
| **T-24 (b)** | Configuração do logger Pino (reutilização e `redact`) | `src/shared/logger/index.ts` | 4–32 | `4:const redactPaths = [`<br>`13:export function createLogger(): Logger {`<br>`16:    redact: {`<br>`32:export const logger: Logger = createLogger();` | VERIFICADO |
| **T-58** | `src/server.ts` como modelo para start do app, signals (`SIGINT`/`SIGTERM`) e encerramento gracioso | `src/server.ts` | 6–27 | `6:async function bootstrap(): Promise<void> {`<br>`13:  const shutdown = async (signal: string): Promise<void> => {`<br>`16:    await prisma.$disconnect();`<br>`20:  process.on('SIGINT', () => void shutdown('SIGINT'));`<br>`21:  process.on('SIGTERM', () => void shutdown('SIGTERM'));` | VERIFICADO |
| **T-25 (a)** | Factory `createPrismaClient()` e instância `prisma` da API | `src/config/database.ts` | 4–10 | `4:export function createPrismaClient(): PrismaClient {`<br>`10:export const prisma: PrismaClient = createPrismaClient();` | VERIFICADO |
| **T-25 (b)** | Instância separada do `PrismaClient` dedicada ao processo do worker | `src/worker.ts` | — | `$ ls -1 src/worker.ts`<br>`ls: cannot access 'src/worker.ts': No such file or directory` | NÃO EXISTE |
| **T-21** | Padrão de módulo (`controller`, `service`, `repository`, `routes`, `schemas`) | `src/modules/orders/` | — | `$ ls -1 src/modules/orders`<br>`order.controller.ts`<br>`order.repository.ts`<br>`order.routes.ts`<br>`order.schemas.ts`<br>`order.service.ts`<br>`order.status.ts` | VERIFICADO |
| **T-39** | Chaves primárias em UUID (`@id @default(uuid()) @db.Char(36)`) | `prisma/schema.prisma` | 26, 41, 57, 75, 100, 117 | `26:  id           String   @id @default(uuid()) @db.Char(36)`<br>`41:  id        String   @id @default(uuid()) @db.Char(36)`<br>`57:  id            String   @id @default(uuid()) @db.Char(36)`<br>`75:  id             String      @id @default(uuid()) @db.Char(36)`<br>`100:  id             String   @id @default(uuid()) @db.Char(36)`<br>`117:  id           String       @id @default(uuid()) @db.Char(36)` | VERIFICADO |
| **T-18** | Validação com schemas Zod e middleware `validate` | `src/modules/orders/order.schemas.ts`<br>`src/middlewares/validate.middleware.ts` | `order.schemas.ts`: 1–34<br>`validate.middleware.ts`: 11–37 | `src/modules/orders/order.schemas.ts:4:export const orderIdParamSchema = z.object({ id: z.string().uuid() });`<br>`src/middlewares/validate.middleware.ts:11:export function validate<S extends Sources>(schemas: S): RequestHandler {` | VERIFICADO |

---

## Detalhamento e Provas por Ponto (1 a 11)

### 1. Hierarquia de Erros (`T-57`: `AppError`, `InvalidStatusTransitionError`, `InsufficientStockError`)

- **Onde está `AppError`:** Definida nas linhas **3 a 16** de `src/shared/errors/app-error.ts` e reexportada na linha **1** de `src/shared/errors/index.ts`.
- **Herança:**
  - `InvalidStatusTransitionError` (`src/shared/errors/http-errors.ts`, linhas **45–53**) estende `ConflictError` (linhas **33–37**), que por sua vez estende `AppError`, herdando indiretamente de `AppError`.
  - `InsufficientStockError` (`src/shared/errors/http-errors.ts`, linhas **55–63**) estende `UnprocessableEntityError` (linhas **39–43**), que por sua vez estende `AppError`, herdando indiretamente de `AppError`.
- **Códigos de erro (strings) e Status HTTP:**
  - `InvalidStatusTransitionError`: `statusCode = 409` (definido em `ConflictError`, linha **35**), `errorCode = 'INVALID_STATUS_TRANSITION'` (linha **49**) e `details = { from, to }` (linha **50**).
  - `InsufficientStockError`: `statusCode = 422` (definido em `UnprocessableEntityError`, linha **41**), `errorCode = 'INSUFFICIENT_STOCK'` (linha **59**) e `details = { unavailable }` (linha **60**).

**Prova (`ls`, `grep -n` e `sed -n`):**
```text
$ ls -1 src/shared/errors/app-error.ts src/shared/errors/http-errors.ts src/shared/errors/index.ts
src/shared/errors/app-error.ts
src/shared/errors/http-errors.ts
src/shared/errors/index.ts

$ grep -n "export class AppError" src/shared/errors/app-error.ts
3:export class AppError extends Error {

$ grep -n "" src/shared/errors/http-errors.ts | sed -n "33,63p"
33:export class ConflictError extends AppError {
34:  constructor(message: string, code = 'CONFLICT', details?: ErrorDetails) {
35:    super(message, 409, code, details);
36:  }
37:}
38:
39:export class UnprocessableEntityError extends AppError {
40:  constructor(message: string, code = 'UNPROCESSABLE_ENTITY', details?: ErrorDetails) {
41:    super(message, 422, code, details);
42:  }
43:}
44:
45:export class InvalidStatusTransitionError extends ConflictError {
46:  constructor(from: string, to: string) {
47:    super(
48:      `Invalid status transition from ${from} to ${to}`,
49:      'INVALID_STATUS_TRANSITION',
50:      { from, to },
51:    );
52:  }
53:}
54:
55:export class InsufficientStockError extends UnprocessableEntityError {
56:  constructor(unavailable: { sku: string; requested: number; available: number }[]) {
57:    super(
58:      'One or more products do not have enough stock',
59:      'INSUFFICIENT_STOCK',
60:      { unavailable },
61:    );
62:  }
63:}
```

---

### 2. Transação em `changeStatus`, Criação de Pedido e Máquina de Estados (`src/modules/orders/order.service.ts` e `src/modules/orders/order.status.ts`)

- **Intervalo real do método `changeStatus`:** Vai da linha **126** (`async changeStatus(`) até a linha **179** (`  }`, logo após o fechamento `});` de `$transaction` na linha **178**) em `src/modules/orders/order.service.ts`.
- **Como a transação é aberta:** Interactive transaction via `this.prisma.$transaction(async (tx) => { ... })` na linha **131**.
- **Tipo do parâmetro de transação (`tx`):** Definido na linha **24** como `type TxClient = Prisma.TransactionClient;`, tipo recebido pelos helpers privados `this.debitStock(tx, order.items)` (chamado na linha **152**, declarado nas linhas **204–207**) e `this.replenishStock(tx, order.items)` (chamado na linha **155**, declarado nas linhas **233–236**).
- **Uso de Repository vs. Prisma direto:** Dentro de `changeStatus`, o `OrderService` **não chama nenhum método de `this.orders` (`OrderRepository`)**; ele invoca diretamente `tx.order.findUnique` (linhas **132** e **169**), `tx.order.update` (linha **158**), `tx.orderStatusHistory.create` (linha **159**) e `tx.product.findMany`/`tx.product.update` (linhas **208**, **226** e **238**).
- **Máquina de estados e regras de estoque (`src/modules/orders/order.status.ts`, linhas 1–37):**
  - O dicionário `transitions` (linhas **3–10**) define as transições permitidas para cada `OrderStatus` (`PENDING` → `PAID`, `CANCELLED`; `PAID` → `PROCESSING`, `CANCELLED`; `PROCESSING` → `SHIPPED`, `CANCELLED`; `SHIPPED` → `DELIVERED`; `DELIVERED` → `[]`; `CANCELLED` → `[]`).
  - `canTransition(from, to)` (linhas **12–14**), `allowedTransitions(from)` (linhas **16–18**), `isTerminal(status)` (linhas **20–22**), `STOCK_DEBIT_TRANSITION` (linhas **24–27**), `shouldDebitStock(from, to)` (linhas **29–31**: `PENDING` → `PAID`) e `shouldReplenishStock(from, to)` (linhas **33–37**: `PAID` ou `PROCESSING` → `CANCELLED`).
- **Criação de pedido (`OrderService.create`, linhas 50–124) e gravação em `order_status_history`:** O método `create` abre `this.prisma.$transaction(async (tx) => { ... })` na linha **58**, cria o pedido via `tx.order.create` (linha **95**) com `status: OrderStatus.PENDING` (linha **99**) e **grava uma linha em `order_status_history`** por escrita aninhada (`history: { create: { fromStatus: null, toStatus: OrderStatus.PENDING, changedById: userId, reason: 'order created' } }`, linhas **106–113**), com `fromStatus: null` (linha **108**).
- **Outros lugares que alteram o status de um pedido:** **Não existe nenhum outro lugar em `src/`** que atualize o status de um pedido além de `OrderService.changeStatus` (linha **158**, única chamada a `order.update` em todo `src/`) e da criação inicial em `OrderService.create` (linhas **95/99**).

**Prova (`grep -n` e `sed -n` de `order.status.ts`, `create`, `changeStatus` e buscas em `src/`):**
```text
$ grep -n "" src/modules/orders/order.status.ts | sed -n "1,37p"
1:import { OrderStatus } from '@prisma/client';
2:
3:const transitions: Readonly<Record<OrderStatus, ReadonlyArray<OrderStatus>>> = {
4:  [OrderStatus.PENDING]: [OrderStatus.PAID, OrderStatus.CANCELLED],
5:  [OrderStatus.PAID]: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
6:  [OrderStatus.PROCESSING]: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
7:  [OrderStatus.SHIPPED]: [OrderStatus.DELIVERED],
8:  [OrderStatus.DELIVERED]: [],
9:  [OrderStatus.CANCELLED]: [],
10:};
11:
12:export function canTransition(from: OrderStatus, to: OrderStatus): boolean {
13:  return transitions[from].includes(to);
14:}
15:
16:export function allowedTransitions(from: OrderStatus): ReadonlyArray<OrderStatus> {
17:  return transitions[from];
18:}
19:
20:export function isTerminal(status: OrderStatus): boolean {
21:  return transitions[status].length === 0;
22:}
23:
24:export const STOCK_DEBIT_TRANSITION = {
25:  from: OrderStatus.PENDING,
26:  to: OrderStatus.PAID,
27:} as const;
28:
29:export function shouldDebitStock(from: OrderStatus, to: OrderStatus): boolean {
30:  return from === STOCK_DEBIT_TRANSITION.from && to === STOCK_DEBIT_TRANSITION.to;
31:}
32:
33:export function shouldReplenishStock(from: OrderStatus, to: OrderStatus): boolean {
34:  return (
35:    to === OrderStatus.CANCELLED && (from === OrderStatus.PAID || from === OrderStatus.PROCESSING)
36:  );
37:}

$ grep -n "type TxClient" src/modules/orders/order.service.ts
24:type TxClient = Prisma.TransactionClient;

$ grep -n -r -E "(prisma|tx)\.order\." src/
src/modules/orders/order.repository.ts:36:      this.prisma.order.findMany({
src/modules/orders/order.repository.ts:42:      this.prisma.order.count({ where }),
src/modules/orders/order.repository.ts:48:    return this.prisma.order.findUnique({
src/modules/orders/order.repository.ts:63:    return this.prisma.order.findUnique({ where: { id } });
src/modules/orders/order.repository.ts:67:    await this.prisma.order.delete({ where: { id } });
src/modules/orders/order.service.ts:95:      const order = await tx.order.create({
src/modules/orders/order.service.ts:132:      const order = await tx.order.findUnique({
src/modules/orders/order.service.ts:158:      await tx.order.update({ where: { id }, data: { status: to } });
src/modules/orders/order.service.ts:169:      const refreshed = await tx.order.findUnique({

$ grep -n -r "orderStatusHistory" src/
src/modules/orders/order.service.ts:159:      await tx.orderStatusHistory.create({

$ grep -n "" src/modules/orders/order.service.ts | sed -n "95,123p"
95:      const order = await tx.order.create({
96:        data: {
97:          orderNumber,
98:          customerId: input.customerId,
99:          status: OrderStatus.PENDING,
100:          subtotalCents,
101:          discountCents: input.discountCents,
102:          totalCents,
103:          notes: input.notes ?? null,
104:          createdById: userId,
105:          items: { create: itemsToCreate },
106:          history: {
107:            create: {
108:              fromStatus: null,
109:              toStatus: OrderStatus.PENDING,
110:              changedById: userId,
111:              reason: 'order created',
112:            },
113:          },
114:        },
115:        include: {
116:          items: { include: { product: { select: { id: true, sku: true, name: true } } } },
117:          history: { orderBy: { changedAt: 'asc' } },
118:          customer: { select: { id: true, name: true, email: true } },
119:        },
120:      });
121:
122:      return order;
123:    });

$ grep -n "" src/modules/orders/order.service.ts | sed -n "126,179p"
126:  async changeStatus(
127:    id: string,
128:    input: UpdateOrderStatusInput,
129:    userId: string,
130:  ): Promise<OrderWithRelations> {
131:    return this.prisma.$transaction(async (tx) => {
132:      const order = await tx.order.findUnique({
133:        where: { id },
134:        include: { items: true },
135:      });
136:      if (!order) throw new NotFoundError('Order');
137:
138:      const from = order.status;
139:      const to = input.toStatus;
140:      if (from === to) {
141:        throw new ConflictError(
142:          `Order is already in ${to} status`,
143:          'INVALID_STATUS_TRANSITION',
144:          { from, to },
145:        );
146:      }
147:      if (!canTransition(from, to)) {
148:        throw new InvalidStatusTransitionError(from, to);
149:      }
150:
151:      if (shouldDebitStock(from, to)) {
152:        await this.debitStock(tx, order.items);
153:      }
154:      if (shouldReplenishStock(from, to)) {
155:        await this.replenishStock(tx, order.items);
156:      }
157:
158:      await tx.order.update({ where: { id }, data: { status: to } });
159:      await tx.orderStatusHistory.create({
160:        data: {
161:          orderId: id,
162:          fromStatus: from,
163:          toStatus: to,
164:          changedById: userId,
165:          reason: input.reason ?? null,
166:        },
167:      });
168:
169:      const refreshed = await tx.order.findUnique({
170:        where: { id },
171:        include: {
172:          items: { include: { product: { select: { id: true, sku: true, name: true } } } },
173:          history: { orderBy: { changedAt: 'asc' } },
174:          customer: { select: { id: true, name: true, email: true } },
175:        },
176:      });
177:      return refreshed!;
178:    });
179:  }
```

---

### 3. Esquema do Banco (`prisma/schema.prisma`): Enums, `User`, `Customer`, `Order` e Colunas

- **Enums `UserRole` e `OrderStatus` (linhas 11–23):**
  - `UserRole` (linhas **11–14**): `ADMIN`, `OPERATOR`.
  - `OrderStatus` (linhas **16–23**): `PENDING`, `PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`.
- **PKs com UUID:** Todas as 6 entidades de domínio (`User`, `Customer`, `Product`, `Order`, `OrderItem`, `OrderStatusHistory`) usam `@id @default(uuid()) @db.Char(36)` nas linhas **26, 41, 57, 75, 100 e 117** (apenas a tabela auxiliar `OrderNumberSequence` usa `id Int @id @default(1)` na linha **134**).
- **Model `User` (linhas 25–38) e ausência de vínculo com `Customer`:**
  - `User` possui apenas os campos escalares `id`, `email`, `passwordHash`, `name`, `role` (`UserRole @default(OPERATOR)`), `createdAt`, `updatedAt` (linhas **26–32**) e as relações `createdOrders Order[] @relation("OrderCreatedBy")` (linha **34**) e `statusHistoryChanges OrderStatusHistory[] @relation("StatusChangedBy")` (linha **35**).
  - Confirmado via `grep -n -i "customer" prisma/schema.prisma`: **não existe nenhum campo nem relação que ligue `User` a `Customer`** (o termo `customer` ocorre apenas em `model Customer`, linhas **40** e **53**, e em `model Order`, linhas **77**, **87** e **92**).
- **Model `Customer`:** **Existe** nas linhas **40–54**, mapeado para `@@map("customers")` (linha **53**), com os campos `id`, `name`, `email`, `phone`, `document`, `address` (`Json`), `createdAt`, `updatedAt` e relação `orders Order[]`.
- **Campos de `Order` (linhas 74–97):**
  - Escalares: `id` (linha **75**), `orderNumber` (`String @unique @db.VarChar(20)`, linha **76**), `customerId` (`String @db.Char(36)`, linha **77**), `status` (`OrderStatus @default(PENDING)`, linha **78**), `subtotalCents` (`Int`, linha **79**), `discountCents` (`Int @default(0)`, linha **80**), `totalCents` (`Int`, linha **81**), `notes` (`String? @db.Text`, linha **82**), `createdById` (`String @db.Char(36)`, linha **83**), `createdAt` (`DateTime @default(now())`, linha **84**) e `updatedAt` (`DateTime @updatedAt`, linha **85**).
  - Confirmado: **existem** `orderNumber` (linha **76**), `customerId` (linha **77**) e `totalCents` (linha **81**), além das relações `customer`, `createdBy`, `items` e `history` (linhas **87–90**).
- **Nomes reais das colunas no banco (`@map` vs `@@map`):**
  - **Não existe nenhum `@map` em campos** em todo o schema; portanto, as colunas reais no MySQL usam `camelCase` (`orderNumber`, `customerId`, `subtotalCents`, `discountCents`, `totalCents`, `stockQuantity`, `fromStatus`, `toStatus`, `createdAt`).
  - **Existe `@@map` apenas nas tabelas** nas linhas **37, 53, 71, 96, 113, 130 e 137** (`users`, `customers`, `products`, `orders`, `order_items`, `order_status_history`, `order_number_sequence`).

**Prova (`grep -n` e `sed -n` de `prisma/schema.prisma`):**
```text
$ grep -n "" prisma/schema.prisma | sed -n "11,23p"
11:enum UserRole {
12:  ADMIN
13:  OPERATOR
14:}
15:
16:enum OrderStatus {
17:  PENDING
18:  PAID
19:  PROCESSING
20:  SHIPPED
21:  DELIVERED
22:  CANCELLED
23:}

$ grep -n "@default(uuid())" prisma/schema.prisma
26:  id           String   @id @default(uuid()) @db.Char(36)
41:  id        String   @id @default(uuid()) @db.Char(36)
57:  id            String   @id @default(uuid()) @db.Char(36)
75:  id             String      @id @default(uuid()) @db.Char(36)
100:  id             String   @id @default(uuid()) @db.Char(36)
117:  id           String       @id @default(uuid()) @db.Char(36)

$ grep -n -i "customer" prisma/schema.prisma
40:model Customer {
53:  @@map("customers")
77:  customerId     String      @db.Char(36)
87:  customer  Customer             @relation(fields: [customerId], references: [id])
92:  @@index([customerId])

$ grep -n "[^@]@map(" prisma/schema.prisma
(nenhuma ocorrência de @map em campos)

$ grep -n "@@map(" prisma/schema.prisma
37:  @@map("users")
53:  @@map("customers")
71:  @@map("products")
96:  @@map("orders")
113:  @@map("order_items")
130:  @@map("order_status_history")
137:  @@map("order_number_sequence")

$ grep -n "" prisma/schema.prisma | sed -n "25,54p"
25:model User {
26:  id           String   @id @default(uuid()) @db.Char(36)
27:  email        String   @unique @db.VarChar(255)
28:  passwordHash String   @db.VarChar(255)
29:  name         String   @db.VarChar(150)
30:  role         UserRole @default(OPERATOR)
31:  createdAt    DateTime @default(now())
32:  updatedAt    DateTime @updatedAt
33:
34:  createdOrders        Order[]              @relation("OrderCreatedBy")
35:  statusHistoryChanges OrderStatusHistory[] @relation("StatusChangedBy")
36:
37:  @@map("users")
38:}
39:
40:model Customer {
41:  id        String   @id @default(uuid()) @db.Char(36)
42:  name      String   @db.VarChar(150)
43:  email     String   @unique @db.VarChar(255)
44:  phone     String   @db.VarChar(32)
45:  document  String   @db.VarChar(20)
46:  address   Json
47:  createdAt DateTime @default(now())
48:  updatedAt DateTime @updatedAt
49:
50:  orders Order[]
51:
52:  @@index([document])
53:  @@map("customers")
54:}

$ grep -n "" prisma/schema.prisma | sed -n "74,97p"
74:model Order {
75:  id             String      @id @default(uuid()) @db.Char(36)
76:  orderNumber    String      @unique @db.VarChar(20)
77:  customerId     String      @db.Char(36)
78:  status         OrderStatus @default(PENDING)
79:  subtotalCents  Int
80:  discountCents  Int         @default(0)
81:  totalCents     Int
82:  notes          String?     @db.Text
83:  createdById    String      @db.Char(36)
84:  createdAt      DateTime    @default(now())
85:  updatedAt      DateTime    @updatedAt
86:
87:  customer  Customer             @relation(fields: [customerId], references: [id])
88:  createdBy User                 @relation("OrderCreatedBy", fields: [createdById], references: [id])
89:  items     OrderItem[]
90:  history   OrderStatusHistory[]
91:
92:  @@index([customerId])
93:  @@index([status])
94:  @@index([createdAt])
95:  @@index([createdById])
96:  @@map("orders")
97:}
```

---

### 4. Papéis (`AuthUser[role]`) e Autenticação (`req.user`)

- **Valores de `AuthUser[role]`:** `'ADMIN' | 'OPERATOR'` na linha **9** de `src/middlewares/auth.middleware.ts`, espelhando o `enum UserRole { ADMIN OPERATOR }` das linhas **11–14** de `prisma/schema.prisma` (confirmado: `ADMIN` existe).
- **Forma do objeto `req.user` (`AuthUser`, linhas 6–10):** `{ id: string; email: string; role: 'ADMIN' | 'OPERATOR' }`.
- **Como `req.user` chega à request:**
  - A interface `Request` do Express é estendida via module augmentation em `express-serve-static-core` nas linhas **12–17** (`user?: AuthUser; id?: string;`).
  - O middleware `authenticate` (linhas **27–47**) lê `req.headers.authorization` (linha **28**), valida o prefixo `'bearer '` (linha **29**), extrai o token (linha **34**), executa `jwt.verify(token, env.JWT_SECRET) as JwtPayload` (linha **41**, onde `JwtPayload` tem `sub`, `email`, `role`, `iat?`, `exp?` nas linhas **19–25**) e popula `req.user = { id: payload.sub, email: payload.email, role: payload.role }` na linha **42**.

**Prova (`grep -n` e `sed -n` de `src/middlewares/auth.middleware.ts`, linhas 6–61):**
```text
$ grep -n -E "(export type AuthUser|role:|req\.user =|export function requireRole)" src/middlewares/auth.middleware.ts
6:export type AuthUser = {
9:  role: 'ADMIN' | 'OPERATOR';
22:  role: AuthUser['role'];
42:    req.user = { id: payload.sub, email: payload.email, role: payload.role };
49:export function requireRole(...roles: AuthUser['role'][]): RequestHandler {

$ grep -n "" src/middlewares/auth.middleware.ts | sed -n "6,61p"
6:export type AuthUser = {
7:  id: string;
8:  email: string;
9:  role: 'ADMIN' | 'OPERATOR';
10:};
11:
12:declare module 'express-serve-static-core' {
13:  interface Request {
14:    user?: AuthUser;
15:    id?: string;
16:  }
17:}
18:
19:type JwtPayload = {
20:  sub: string;
21:  email: string;
22:  role: AuthUser['role'];
23:  iat?: number;
24:  exp?: number;
25:};
26:
27:export const authenticate: RequestHandler = (req, _res, next) => {
28:  const header = req.headers.authorization;
29:  if (!header || !header.toLowerCase().startsWith('bearer ')) {
30:    next(new UnauthorizedError('Missing or invalid Authorization header'));
31:    return;
32:  }
33:
34:  const token = header.slice(7).trim();
35:  if (!token) {
36:    next(new UnauthorizedError('Missing bearer token'));
37:    return;
38:  }
39:
40:  try {
41:    const payload = jwt.verify(token, env.JWT_SECRET) as JwtPayload;
42:    req.user = { id: payload.sub, email: payload.email, role: payload.role };
43:    next();
44:  } catch {
45:    next(new UnauthorizedError('Invalid or expired token'));
46:  }
47:};
48:
49:export function requireRole(...roles: AuthUser['role'][]): RequestHandler {
50:  return (req, _res, next) => {
51:    if (!req.user) {
52:      next(new UnauthorizedError());
53:      return;
54:    }
55:    if (!roles.includes(req.user.role)) {
56:      next(new ForbiddenError('Insufficient permissions'));
57:      return;
58:    }
59:    next();
60:  };
61:}
```

---

### 5. Formato de Resposta (Erro e Paginação Real)

- **Formato JSON de Erro (`src/middlewares/error.middleware.ts`, linhas 14–65):**
  - Bloco `if (err instanceof AppError)` nas **linhas 15–24** (com a chamada `res.status(err.statusCode).json({ ... })` nas linhas **16–22**): retorna status `err.statusCode` e corpo `{ error: { code: err.errorCode, message: err.message, ...(err.details !== undefined ? { details: err.details } : {}) } }`.
  - Bloco `if (err instanceof ZodError)` nas **linhas 26–35**: retorna status `400` e corpo `{ error: { code: 'VALIDATION_ERROR', message: 'Validation failed', details: formatZodIssues(err) } }`.
  - Bloco `if (err instanceof Prisma.PrismaClientKnownRequestError)` nas **linhas 37–54**: `P2002` retorna `409` com `code: 'CONFLICT'` e `P2025` retorna `404` com `code: 'NOT_FOUND'`.
  - Erros não tratados nas **linhas 56–65**: registra log via `logger.error` e retorna `500` com `{ error: { code: 'INTERNAL_SERVER_ERROR', message: 'Internal server error' } }`.
- **Formato Real de Resposta Paginada no Controller de Orders:**
  - `OrderRepository.list` (`src/modules/orders/order.repository.ts`, linhas **33–45**) retorna internamente `{ items: Order[]; total: number }` para o service.
  - `OrderService.list` (`src/modules/orders/order.service.ts`, linhas **32–42**) chama `paginated(items, query.page, query.pageSize, total)` na linha **41**.
  - A função `paginated` (`src/shared/http/response.ts`, linhas **1–24**) constrói o envelope `PaginatedResponse<T>` no formato `{ data: T[], pagination: { page: number, pageSize: number, total: number, totalPages: number } }`.
  - `OrderController.list` (`src/modules/orders/order.controller.ts`, linhas **9–17**) responde com `res.status(200).json(result)` na linha **13**, formato validado também nas linhas **187–195** de `tests/orders.test.ts` (`paid.body.data`, `pending.body.pagination.total`).

**Prova (`sed -n` e `grep -n` de `error.middleware.ts`, `response.ts`, `order.service.ts`, `order.controller.ts` e `tests/orders.test.ts`):**
```text
$ grep -n "" src/middlewares/error.middleware.ts | sed -n "14,25p"
14:export const errorMiddleware: ErrorRequestHandler = (err, req, res, _next) => {
15:  if (err instanceof AppError) {
16:    res.status(err.statusCode).json({
17:      error: {
18:        code: err.errorCode,
19:        message: err.message,
20:        ...(err.details !== undefined ? { details: err.details } : {}),
21:      },
22:    });
23:    return;
24:  }
25:

$ grep -n "" src/shared/http/response.ts | sed -n "1,24p"
1:export type Pagination = {
2:  page: number;
3:  pageSize: number;
4:  total: number;
5:  totalPages: number;
6:};
7:
8:export type PaginatedResponse<T> = {
9:  data: T[];
10:  pagination: Pagination;
11:};
12:
13:export function buildPagination(page: number, pageSize: number, total: number): Pagination {
14:  return {
15:    page,
16:    pageSize,
17:    total,
18:    totalPages: pageSize === 0 ? 0 : Math.ceil(total / pageSize),
19:  };
20:}
21:
22:export function paginated<T>(data: T[], page: number, pageSize: number, total: number): PaginatedResponse<T> {
23:  return { data, pagination: buildPagination(page, pageSize, total) };
24:}

$ grep -n "" src/modules/orders/order.service.ts | sed -n "32,42p"
32:  async list(query: ListOrdersQuery): Promise<PaginatedResponse<Order>> {
33:    const { items, total } = await this.orders.list({
34:      status: query.status,
35:      customerId: query.customerId,
36:      from: query.from,
37:      to: query.to,
38:      skip: (query.page - 1) * query.pageSize,
39:      take: query.pageSize,
40:    });
41:    return paginated(items, query.page, query.pageSize, total);
42:  }

$ grep -n "" src/modules/orders/order.controller.ts | sed -n "9,17p"
9:  list: RequestHandler = async (req, res, next) => {
10:    try {
11:      const query = req.query as unknown as ListOrdersQuery;
12:      const result = await this.orders.list(query);
13:      res.status(200).json(result);
14:    } catch (err) {
15:      next(err);
16:    }
17:  };

$ grep -n "" tests/orders.test.ts | sed -n "187,195p"
187:    expect(paid.body.data).toHaveLength(1);
188:    expect(paid.body.data[0].id).toBe(ids[0]);
189:
190:    const pending = await request(app)
191:      .get('/api/v1/orders?status=PENDING')
192:      .set('Authorization', `Bearer ${token}`);
193:    expect(pending.body.data).toHaveLength(2);
194:    expect(pending.body.pagination.total).toBe(2);
195:  });
```

---

### 6. `package.json`, `tsconfig.build.json`, Versão do Node, `fetch` Nativo e Ausência de Clientes HTTP / Observabilidade

- **Versão do Node:** Declarada nas linhas **7–9** de `package.json` como `"engines": { "node": ">=20" }` (com `@types/node` em `"20.17.6"` na linha **39**), e o arquivo `.nvmrc` **não existe** na raiz do projeto.
- **Scripts de execução e build (`package.json`, linhas 10–21, e `tsconfig.build.json`, linhas 1–11):**
  - `"dev": "tsx watch --env-file=.env src/server.ts"` (linha **11**), `"build": "tsc -p tsconfig.build.json"` (linha **12**) e `"start": "node --env-file=.env dist/server.js"` (linha **13**).
  - `tsconfig.build.json` (linhas **1–11**) define `"rootDir": "./src"` (linha **4**), `"outDir": "./dist"` (linha **5**), `"include": ["src/**/*.ts"]` (linha **9**) e `"exclude": ["node_modules", "dist", "tests", "prisma", "**/*.test.ts"]` (linha **10**).
- **Framework de teste:** `vitest` versão `"2.1.4"` (linha **52**) e `supertest` versão `"7.0.0"` (linha **49**), com os scripts `"test": "vitest run"` (linha **17**) e `"test:watch": "vitest"` (linha **18**).
- **Dependências Pino, Zod e Prisma em `package.json`:**
  - `@prisma/client`: `"5.22.0"` (`dependencies`, linha **26**) e `prisma`: `"5.22.0"` (`devDependencies`, linha **48**).
  - `pino`: `"9.5.0"` (`dependencies`, linha **30**), `pino-http`: `"10.3.0"` (linha **31**) e `pino-pretty`: `"11.3.0"` (`devDependencies`, linha **46**).
  - `zod`: `"3.23.8"` (`dependencies`, linha **33**).
- **Disponibilidade de `fetch` nativo:** **Sim.** A função global `globalThis.fetch` está **disponível** nativamente no Node; a verificação em runtime foi realizada em **Node `v21.7.3`** (`node: v21.7.3 typeof fetch: function`), enquanto o `package.json` (linhas **7–9**) aceita `"node": ">=20"`.
- **Prova de ausência de clientes HTTP e bibliotecas de observabilidade (`axios`, `got`, `undici`, `node-fetch`, `prom-client`, `opentelemetry`, `datadog`):** Confirmado via `grep -n -i -E` em `package.json` com retorno vazio `(no matches)`.

**Prova (`ls`, `grep -n`, `node -e` e `sed -n` de `package.json` e `tsconfig.build.json`):**
```text
$ ls -1 .nvmrc
ls: cannot access '.nvmrc': No such file or directory

$ grep -n -i -E "(axios|got|undici|node-fetch|prom-client|opentelemetry|datadog)" package.json
(no matches)

$ node -e 'console.log("node:", process.version, "typeof fetch:", typeof globalThis.fetch)'
node: v21.7.3 typeof fetch: function

$ grep -n "" package.json | sed -n "7,53p"
7:  "engines": {
8:    "node": ">=20"
9:  },
10:  "scripts": {
11:    "dev": "tsx watch --env-file=.env src/server.ts",
12:    "build": "tsc -p tsconfig.build.json",
13:    "start": "node --env-file=.env dist/server.js",
14:    "db:migrate": "prisma migrate dev",
15:    "db:reset": "prisma migrate reset --force",
16:    "db:seed": "tsx --env-file=.env prisma/seed.ts",
17:    "test": "vitest run",
18:    "test:watch": "vitest",
19:    "lint": "eslint . --ext .ts",
20:    "format": "prettier --write ."
21:  },
22:  "prisma": {
23:    "seed": "tsx prisma/seed.ts"
24:  },
25:  "dependencies": {
26:    "@prisma/client": "5.22.0",
27:    "bcrypt": "5.1.1",
28:    "express": "4.21.1",
29:    "jsonwebtoken": "9.0.2",
30:    "pino": "9.5.0",
31:    "pino-http": "10.3.0",
32:    "uuid": "11.0.3",
33:    "zod": "3.23.8"
34:  },
35:  "devDependencies": {
36:    "@types/bcrypt": "5.0.2",
37:    "@types/express": "4.17.21",
38:    "@types/jsonwebtoken": "9.0.7",
39:    "@types/node": "20.17.6",
40:    "@types/supertest": "6.0.2",
41:    "@types/uuid": "10.0.0",
42:    "@typescript-eslint/eslint-plugin": "8.13.0",
43:    "@typescript-eslint/parser": "8.13.0",
44:    "eslint": "8.57.1",
45:    "eslint-config-prettier": "9.1.0",
46:    "pino-pretty": "11.3.0",
47:    "prettier": "3.3.3",
48:    "prisma": "5.22.0",
49:    "supertest": "7.0.0",
50:    "tsx": "4.19.2",
51:    "typescript": "5.6.3",
52:    "vitest": "2.1.4"
53:  }

$ grep -n "" tsconfig.build.json | sed -n "1,11p"
1:{
2:  "extends": "./tsconfig.json",
3:  "compilerOptions": {
4:    "rootDir": "./src",
5:    "outDir": "./dist",
6:    "sourceMap": false,
7:    "declaration": false
8:  },
9:  "include": ["src/**/*.ts"],
10:  "exclude": ["node_modules", "dist", "tests", "prisma", "**/*.test.ts"]
11:}
```

---

### 7. Execução dos Testes (`tests/orders.test.ts`, `tests/setup.ts`, `tests/helpers/factories.ts`, `vitest.config.ts`, `.env.example`)

- **Framework e Runner (`vitest.config.ts`, linhas 1–19):**
  - Roda via **Vitest** (`vitest run`) em ambiente `node` (linha **6**), incluindo `tests/**/*.test.ts` (linha **7**).
  - Executa de forma **sequencial em processo único** (`fileParallelism: false` na linha **11**, `pool: 'forks'` na linha **12**, `singleFork: true` na linha **15**) e carrega `setupFiles: ['tests/setup.ts']` (linha **10**).
- **Setup e Banco de Teste (`tests/setup.ts`, linhas 1–20, e `.env.example`, linha 5):**
  - Importa a instância real `prisma` de `../src/config/database.js` (linha **2**), conectada ao MySQL configurado em `DATABASE_URL` (`.env.example`, linha **5**: `DATABASE_URL="mysql://oms_user:oms_password@localhost:3306/oms"`).
  - Executa `await prisma.$connect()` no `beforeAll` (linhas **4–6**), limpa todas as 7 tabelas com `deleteMany()` no `beforeEach` (linhas **8–16**) e executa `await prisma.$disconnect()` no `afterAll` (linhas **18–20**).
- **Como `tests/orders.test.ts` e `tests/helpers/factories.ts` exercitam a aplicação:**
  - `getTestApp()` (`tests/helpers/factories.ts`, linhas **10–15**) instancia `buildApp({ prisma })` (linha **12**).
  - `createTestUser` (`tests/helpers/factories.ts`, linhas **17–31**) cria o usuário no banco e `loginAndGetToken` (linhas **33–40**) autentica via `request(app).post('/api/v1/auth/login').send({ email, password })` (linha **35**).
  - `tests/orders.test.ts` (linhas **187–195**) valida as respostas HTTP da listagem paginada (`paid.body.data`, `pending.body.data` e `pending.body.pagination.total`).

**Prova (`ls`, `grep -n` e `sed -n` de `vitest.config.ts`, `tests/setup.ts`, `.env.example`, `tests/helpers/factories.ts` e `tests/orders.test.ts`):**
```text
$ ls -1 vitest.config.ts tests/setup.ts tests/orders.test.ts tests/helpers/factories.ts .env.example
.env.example
tests/helpers/factories.ts
tests/orders.test.ts
tests/setup.ts
vitest.config.ts

$ grep -n "" .env.example | sed -n "5p"
5:DATABASE_URL="mysql://oms_user:oms_password@localhost:3306/oms"

$ grep -n "" vitest.config.ts | sed -n "1,19p"
1:import { defineConfig } from 'vitest/config';
2:
3:export default defineConfig({
4:  test: {
5:    globals: false,
6:    environment: 'node',
7:    include: ['tests/**/*.test.ts'],
8:    testTimeout: 30000,
9:    hookTimeout: 30000,
10:    setupFiles: ['tests/setup.ts'],
11:    fileParallelism: false,
12:    pool: 'forks',
13:    poolOptions: {
14:      forks: {
15:        singleFork: true,
16:      },
17:    },
18:  },
19:});

$ grep -n "" tests/setup.ts | sed -n "1,20p"
1:import { afterAll, beforeAll, beforeEach } from 'vitest';
2:import { prisma } from '../src/config/database.js';
3:
4:beforeAll(async () => {
5:  await prisma.$connect();
6:});
7:
8:beforeEach(async () => {
9:  await prisma.orderStatusHistory.deleteMany();
10:  await prisma.orderItem.deleteMany();
11:  await prisma.order.deleteMany();
12:  await prisma.orderNumberSequence.deleteMany();
13:  await prisma.product.deleteMany();
14:  await prisma.customer.deleteMany();
15:  await prisma.user.deleteMany();
16:});
17:
18:afterAll(async () => {
19:  await prisma.$disconnect();
20:});

$ grep -n "" tests/helpers/factories.ts | sed -n "10,40p"
10:export function getTestApp(): Express {
11:  if (!cachedApp) {
12:    cachedApp = buildApp({ prisma });
13:  }
14:  return cachedApp;
15:}
16:
17:export async function createTestUser(
18:  overrides: Partial<{ email: string; password: string; name: string; role: 'ADMIN' | 'OPERATOR' }> = {},
19:): Promise<{ user: User; password: string }> {
20:  const password = overrides.password ?? 'password123';
21:  const passwordHash = await bcrypt.hash(password, 10);
22:  const user = await prisma.user.create({
23:    data: {
24:      email: overrides.email ?? `user-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@test.local`,
25:      name: overrides.name ?? 'Test User',
26:      passwordHash,
27:      role: overrides.role ?? 'OPERATOR',
28:    },
29:  });
30:  return { user, password };
31:}
32:
33:export async function loginAndGetToken(email: string, password: string): Promise<string> {
34:  const app = getTestApp();
35:  const res = await request(app).post('/api/v1/auth/login').send({ email, password });
36:  if (res.status !== 200) {
37:    throw new Error(`login failed: ${res.status} ${JSON.stringify(res.body)}`);
38:  }
39:  return res.body.tokens.accessToken as string;
40:}

$ grep -n "" tests/orders.test.ts | sed -n "187,195p"
187:    expect(paid.body.data).toHaveLength(1);
188:    expect(paid.body.data[0].id).toBe(ids[0]);
189:
190:    const pending = await request(app)
191:      .get('/api/v1/orders?status=PENDING')
192:      .set('Authorization', `Bearer ${token}`);
193:    expect(pending.body.data).toHaveLength(2);
194:    expect(pending.body.pagination.total).toBe(2);
195:  });
```

---

### 8. Composição e Roteamento (`src/app.ts` e `src/routes/index.ts`)

- **Onde o tipo `Controllers` é declarado:** Em `src/routes/index.ts`, linhas **13–19** (`export type Controllers = { auth: AuthController; users: UserController; customers: CustomerController; products: ProductController; orders: OrderController; };`), sendo importado em `src/app.ts` na linha **19** (`import { buildApiRouter, type Controllers } from './routes/index.js';`).
- **Como `buildApiRouter` monta os sub-roteadores (`src/routes/index.ts`, linhas 21–31):** Instancia `Router()` na linha **22** e registra `/auth` (linha **24**), `/users` (linha **25**), `/customers` (linha **26**), `/products` (linha **27**) e `/orders` (linha **28**).
- **Como `controllers`, `services` e `repositories` são instanciados (`src/app.ts`, `buildControllers`, linhas 26–53):**
  - Recebe `prisma: PrismaClient` (linha **26**) e instancia manualmente em cadeia cada módulo: `new *Repository(prisma)` → `new *Service(...)` → `new *Controller(*Service)`.
  - Caso especial em `orders` (linhas **42–44**): `OrderService` recebe tanto `orderRepository` quanto `prisma` (`new OrderService(orderRepository, prisma)` na linha **43**) para abrir `this.prisma.$transaction(...)`.
  - Retorna o objeto `{ auth, users, customers, products, orders }` tipado como `Controllers` (linhas **46–52**).
- **Como são passados ao `buildApiRouter` (`src/app.ts`, `buildApp`, linhas 55–76):**
  - `buildApp(deps: AppDependencies)` chama `const controllers = buildControllers(deps.prisma);` na linha **66** e registra `app.use('/api/v1', buildApiRouter(controllers));` na linha **67**.

**Prova (`sed -n` de `src/routes/index.ts` completo e de `src/app.ts`):**
```text
$ grep -n "" src/routes/index.ts | sed -n "1,31p"
1:import { Router } from 'express';
2:import type { AuthController } from '../modules/auth/auth.controller.js';
3:import type { UserController } from '../modules/users/user.controller.js';
4:import type { CustomerController } from '../modules/customers/customer.controller.js';
5:import type { ProductController } from '../modules/products/product.controller.js';
6:import type { OrderController } from '../modules/orders/order.controller.js';
7:import { buildAuthRouter } from '../modules/auth/auth.routes.js';
8:import { buildUserRouter } from '../modules/users/user.routes.js';
9:import { buildCustomerRouter } from '../modules/customers/customer.routes.js';
10:import { buildProductRouter } from '../modules/products/product.routes.js';
11:import { buildOrderRouter } from '../modules/orders/order.routes.js';
12:
13:export type Controllers = {
14:  auth: AuthController;
15:  users: UserController;
16:  customers: CustomerController;
17:  products: ProductController;
18:  orders: OrderController;
19:};
20:
21:export function buildApiRouter(controllers: Controllers): Router {
22:  const router = Router();
23:
24:  router.use('/auth', buildAuthRouter(controllers.auth));
25:  router.use('/users', buildUserRouter(controllers.users));
26:  router.use('/customers', buildCustomerRouter(controllers.customers));
27:  router.use('/products', buildProductRouter(controllers.products));
28:  router.use('/orders', buildOrderRouter(controllers.orders));
29:
30:  return router;
31:}

$ grep -n "" src/app.ts | sed -n "19,76p"
19:import { buildApiRouter, type Controllers } from './routes/index.js';
20:import { NotFoundError } from './shared/errors/index.js';
21:
22:export type AppDependencies = {
23:  prisma: PrismaClient;
24:};
25:
26:export function buildControllers(prisma: PrismaClient): Controllers {
27:  const userRepository = new UserRepository(prisma);
28:  const userService = new UserService(userRepository);
29:  const userController = new UserController(userService);
30:
31:  const authService = new AuthService(userRepository, userService);
32:  const authController = new AuthController(authService, userService);
33:
34:  const customerRepository = new CustomerRepository(prisma);
35:  const customerService = new CustomerService(customerRepository);
36:  const customerController = new CustomerController(customerService);
37:
38:  const productRepository = new ProductRepository(prisma);
39:  const productService = new ProductService(productRepository);
40:  const productController = new ProductController(productService);
41:
42:  const orderRepository = new OrderRepository(prisma);
43:  const orderService = new OrderService(orderRepository, prisma);
44:  const orderController = new OrderController(orderService);
45:
46:  return {
47:    auth: authController,
48:    users: userController,
49:    customers: customerController,
50:    products: productController,
51:    orders: orderController,
52:  };
53:}
54:
55:export function buildApp(deps: AppDependencies): Express {
56:  const app = express();
57:
58:  app.disable('x-powered-by');
59:  app.use(express.json({ limit: '1mb' }));
60:  app.use(requestLogger);
61:
62:  app.get('/health', (_req, res) => {
63:    res.status(200).json({ status: 'ok' });
64:  });
65:
66:  const controllers = buildControllers(deps.prisma);
67:  app.use('/api/v1', buildApiRouter(controllers));
68:
69:  app.use((req, _res, next) => {
70:    next(new NotFoundError(`Route ${req.method} ${req.originalUrl}`));
71:  });
72:
73:  app.use(errorMiddleware);
74:
75:  return app;
76:}
```

---

### 9. Rotas de Pedidos e de Usuários: Ordem de `authenticate`, `requireRole` e `validate` (`src/modules/orders/order.routes.ts` e `src/modules/users/user.routes.ts`)

- **Em `src/modules/orders/order.routes.ts` (linhas 1–27):**
  - `authenticate` é aplicado globalmente a todas as rotas do módulo na linha **14** via `router.use(authenticate);`.
  - `validate(...)` é aplicado individualmente por rota nas linhas **16, 17, 18, 21 e 24** (`validate({ query: ... })`, `validate({ params: ... })`, `validate({ body: ... })` ou `validate({ params: ..., body: ... })`) antes do handler do controller.
  - `requireRole` **não é importado nem utilizado** em `order.routes.ts`.
- **Em `src/modules/users/user.routes.ts` (linhas 1–21):**
  - É o único roteador do código atual que utiliza `requireRole('ADMIN')`.
  - Na rota `router.get('/:id', ...)` (linhas **12–18**), os middlewares são encadeados exatamente nesta ordem: `authenticate` (linha **14**) → `requireRole('ADMIN')` (linha **15**) → `validate({ params: idParamSchema })` (linha **16**) → `controller.getById` (linha **17**).

**Prova (`sed -n` de `order.routes.ts`, de `user.routes.ts` e `grep -n -r "requireRole" src/`):**
```text
$ grep -n "" src/modules/orders/order.routes.ts | sed -n "1,27p"
1:import { Router } from 'express';
2:import { authenticate } from '../../middlewares/auth.middleware.js';
3:import { validate } from '../../middlewares/validate.middleware.js';
4:import {
5:  createOrderSchema,
6:  listOrdersQuerySchema,
7:  orderIdParamSchema,
8:  updateOrderStatusSchema,
9:} from './order.schemas.js';
10:import type { OrderController } from './order.controller.js';
11:
12:export function buildOrderRouter(controller: OrderController): Router {
13:  const router = Router();
14:  router.use(authenticate);
15:
16:  router.get('/', validate({ query: listOrdersQuerySchema }), controller.list);
17:  router.get('/:id', validate({ params: orderIdParamSchema }), controller.getById);
18:  router.post('/', validate({ body: createOrderSchema }), controller.create);
19:  router.patch(
20:    '/:id/status',
21:    validate({ params: orderIdParamSchema, body: updateOrderStatusSchema }),
22:    controller.changeStatus,
23:  );
24:  router.delete('/:id', validate({ params: orderIdParamSchema }), controller.delete);
25:
26:  return router;
27:}

$ grep -n "" src/modules/users/user.routes.ts | sed -n "1,21p"
1:import { Router } from 'express';
2:import { z } from 'zod';
3:import { authenticate, requireRole } from '../../middlewares/auth.middleware.js';
4:import { validate } from '../../middlewares/validate.middleware.js';
5:import type { UserController } from './user.controller.js';
6:
7:const idParamSchema = z.object({ id: z.string().uuid() });
8:
9:export function buildUserRouter(controller: UserController): Router {
10:  const router = Router();
11:
12:  router.get(
13:    '/:id',
14:    authenticate,
15:    requireRole('ADMIN'),
16:    validate({ params: idParamSchema }),
17:    controller.getById,
18:  );
19:
20:  return router;
21:}

$ grep -n -r "requireRole" src/
src/modules/users/user.routes.ts:3:import { authenticate, requireRole } from '../../middlewares/auth.middleware.js';
src/modules/users/user.routes.ts:15:    requireRole('ADMIN'),
src/middlewares/auth.middleware.ts:49:export function requireRole(...roles: AuthUser['role'][]): RequestHandler {
```

---

### 10. `src/config/database.ts` e Validação de Ambiente (`src/config/env.ts`)

- **Dependência de `env` em `createPrismaClient()` (`src/config/database.ts`, linhas 1–10):**
  - Importa `{ env } from './env.js'` na linha **2** e lê `env.NODE_ENV` na linha **6** (`log: env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error']`), além de instanciar imediatamente `export const prisma: PrismaClient = createPrismaClient();` na linha **10**.
- **Variáveis exigidas por `src/config/env.ts` (linhas 1–27):**
  - Ao ser importado, `env.ts` executa imediatamente `export const env: Env = loadEnv();` (linha **27**), validando `process.env` com `envSchema.safeParse(process.env)` (linha **15**) e chamando `process.exit(1)` (linha **22**) se falhar.
  - Embora `NODE_ENV`, `PORT`, `LOG_LEVEL` e `JWT_EXPIRES_IN` possuam `.default(...)` (linhas **4, 5, 6 e 9**), o schema **exige obrigatoriamente** `DATABASE_URL: z.string().min(1, 'DATABASE_URL is required')` (linha **7**) **e `JWT_SECRET: z.string().min(16, 'JWT_SECRET must be at least 16 characters')` (linha **8**)**.

**Prova (`sed -n` de `src/config/database.ts` e `src/config/env.ts`):**
```text
$ grep -n "" src/config/database.ts | sed -n "1,10p"
1:import { PrismaClient } from '@prisma/client';
2:import { env } from './env.js';
3:
4:export function createPrismaClient(): PrismaClient {
5:  return new PrismaClient({
6:    log: env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
7:  });
8:}
9:
10:export const prisma: PrismaClient = createPrismaClient();

$ grep -n "" src/config/env.ts | sed -n "1,27p"
1:import { z } from 'zod';
2:
3:const envSchema = z.object({
4:  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
5:  PORT: z.coerce.number().int().positive().default(3000),
6:  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
7:  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),
8:  JWT_SECRET: z.string().min(16, 'JWT_SECRET must be at least 16 characters'),
9:  JWT_EXPIRES_IN: z.string().default('8h'),
10:});
11:
12:export type Env = z.infer<typeof envSchema>;
13:
14:function loadEnv(): Env {
15:  const parsed = envSchema.safeParse(process.env);
16:  if (!parsed.success) {
17:    const issues = parsed.error.issues
18:      .map((issue) => `  - ${issue.path.join('.')}: ${issue.message}`)
19:      .join('\n');
20:    // eslint-disable-next-line no-console
21:    console.error(`Invalid environment configuration:\n${issues}`);
22:    process.exit(1);
23:  }
24:  return parsed.data;
25:}
26:
27:export const env: Env = loadEnv();
```

---

### 11. Logger Pino e Configuração de `redact` (`src/shared/logger/index.ts`)

- **Configuração de `redact`:** **Existe** nas linhas **4–11** e **16–19** de `src/shared/logger/index.ts`.
- **Caminhos mascarados (`redactPaths`, linhas 4–11):** `'req.headers.authorization'`, `'req.headers.cookie'`, `'*.password'`, `'*.passwordHash'`, `'*.token'`, `'*.accessToken'`, substituídos por `censor: '[REDACTED]'` (linha **18**).
- **Metadados base (`base`, linha 20):** Fixa `base: { service: 'order-management-api', env: env.NODE_ENV }`.

**Prova (`sed -n "1,32p" src/shared/logger/index.ts`):**
```text
$ grep -n "" src/shared/logger/index.ts | sed -n "1,32p"
1:import pino, { type Logger } from 'pino';
2:import { env } from '../../config/env.js';
3:
4:const redactPaths = [
5:  'req.headers.authorization',
6:  'req.headers.cookie',
7:  '*.password',
8:  '*.passwordHash',
9:  '*.token',
10:  '*.accessToken',
11:];
12:
13:export function createLogger(): Logger {
14:  return pino({
15:    level: env.LOG_LEVEL,
16:    redact: {
17:      paths: redactPaths,
18:      censor: '[REDACTED]',
19:    },
20:    base: { service: 'order-management-api', env: env.NODE_ENV },
21:    timestamp: pino.stdTimeFunctions.isoTime,
22:    transport:
23:      env.NODE_ENV === 'development'
24:        ? {
25:            target: 'pino-pretty',
26:            options: { colorize: true, singleLine: false, translateTime: 'HH:MM:ss.l' },
27:          }
28:        : undefined,
29:  });
30:}
31:
32:export const logger: Logger = createLogger();
```

---

## Parte B: O que o FDD vai precisar e a reunião não definiu

| Ponto | Fato verificado no código | Arquivo e Linha(s) | Saída crua (`grep -n` / `sed -n`) | Situação |
| :--- | :--- | :--- | :--- | :--- |
| **Prefixo de rotas da API e `Controllers`** | O prefixo global é `/api/v1`, montado em `src/app.ts` sobre `buildApiRouter(controllers)`; o tipo `Controllers` e os sub-roteadores são declarados em `src/routes/index.ts` | `src/app.ts` (linhas 19, 66–67)<br>`src/routes/index.ts` (linhas 13–31) | `src/app.ts:67:  app.use('/api/v1', buildApiRouter(controllers));`<br>`src/routes/index.ts:13:export type Controllers = {`<br>`src/routes/index.ts:21:export function buildApiRouter(controllers: Controllers): Router {` | VERIFICADO |
| **Enums `UserRole` e `OrderStatus` e Máquina de Estados** | `UserRole`: `ADMIN`, `OPERATOR`. `OrderStatus`: `PENDING`, `PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`. Dicionário `transitions` e funções `canTransition`, `shouldDebitStock` e `shouldReplenishStock` em `order.status.ts` | `prisma/schema.prisma` (linhas 11–23)<br>`src/modules/orders/order.status.ts` (linhas 1–37) | `prisma/schema.prisma:11:enum UserRole {`<br>`prisma/schema.prisma:16:enum OrderStatus {`<br>`src/modules/orders/order.status.ts:3:const transitions: Readonly<Record<OrderStatus, ReadonlyArray<OrderStatus>>> = {`<br>`src/modules/orders/order.status.ts:12:export function canTransition(from: OrderStatus, to: OrderStatus): boolean {`<br>`src/modules/orders/order.status.ts:29:export function shouldDebitStock(from: OrderStatus, to: OrderStatus): boolean {`<br>`src/modules/orders/order.status.ts:33:export function shouldReplenishStock(from: OrderStatus, to: OrderStatus): boolean {` | VERIFICADO |
| **Convenções de nomes no Prisma** | Tabelas usam `@@map("snake_case_plural")`; campos usam `camelCase` sem `@map` | `prisma/schema.prisma` (linhas 37, 53, 71, 96, 113, 130, 137) | `96:  @@map("orders")` / `(nenhuma ocorrência de @map em campos)` | VERIFICADO |
| **Envelope de Erro e de Paginação** | Erro (`AppError`, linhas 15–24, com `res.status(...).json(...)` nas linhas 16–22): `{ error: { code, message, details? } }`. Paginação HTTP: `{ data: T[], pagination: { page, pageSize, total, totalPages } }` | `src/middlewares/error.middleware.ts` (linhas 15–24)<br>`src/shared/http/response.ts` (linhas 1–24) | `src/middlewares/error.middleware.ts:15:  if (err instanceof AppError) {`<br>`src/shared/http/response.ts:22:export function paginated<T>(data: T[], page: number, pageSize: number, total: number): PaginatedResponse<T> {` | VERIFICADO |
| **Observabilidade e Clientes HTTP** | Não há bibliotecas de cliente HTTP (`axios`, `got`, `undici`, `node-fetch`) nem métricas/tracing (`prom-client`, `opentelemetry`, `datadog`) em `package.json`; apenas `pino` e `pino-http` | `package.json` (linhas 25–53) | `$ grep -n -i -E "(axios\|got\|undici\|node-fetch\|prom-client\|opentelemetry\|datadog)" package.json`<br>`(no matches)` | VERIFICADO |

---

## Parte C: Ganchos mencionados na reunião, mas inexistentes no código atual

| ID | O que a reunião disse / Gancho | Caminho procurado | Saída crua (`ls` / `grep -n`) | Situação |
| :--- | :--- | :--- | :--- | :--- |
| **T-34** | Função helper `publishWebhookEvent(tx, ...)` chamada dentro de `changeStatus` | `src/modules/orders/order.service.ts` | `$ grep -n "publishWebhookEvent" src/ -r`<br>`(no matches)` | NÃO EXISTE |
| **T-10** | Script `npm run worker` no `package.json` e entrypoint `src/worker.ts` | `package.json`, `src/worker.ts` | `$ ls -1 src/worker.ts`<br>`ls: cannot access 'src/worker.ts': No such file or directory`<br>`$ grep -n "\"worker\"" package.json`<br>`(nenhuma ocorrência de worker em package.json)` | NÃO EXISTE |
| **T-21 / T-22** | Módulo `src/modules/webhooks/` (incluindo `webhook.worker.ts` ou `webhook.processor.ts`) | `src/modules/webhooks/` | `$ ls -1 src/modules/webhooks`<br>`ls: cannot access 'src/modules/webhooks': No such file or directory` | NÃO EXISTE |
| **T-25 (b)** | Instância separada do `PrismaClient` para o processo do worker (apenas o factory `createPrismaClient()` existe em `src/config/database.ts:4`) | `src/worker.ts` | `$ ls -1 src/worker.ts`<br>`ls: cannot access 'src/worker.ts': No such file or directory` | NÃO EXISTE |
| **T-23** | Classes/códigos de erro com prefixo `WEBHOOK_*` (`WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL`, etc.) | `src/shared/errors/http-errors.ts` | `$ grep -n "WEBHOOK_" src/ -r`<br>`(no matches)` | NÃO EXISTE |
| **T-05, T-14** | Tabelas/models de webhook (`webhook_outbox`, `webhook_dead_letter`, assinaturas/endpoints) | `prisma/schema.prisma` | `$ grep -n "webhook" prisma/schema.prisma`<br>`(no matches)` | NÃO EXISTE |

---

## Divergências entre reunião e código

| ID (`_work/CATALOGO.md`) | O que a reunião falou | O que existe no código real | Evidência (`grep -n` e linha) |
| :--- | :--- | :--- | :--- |
| **T-56, T-07, T-61** | Falou nomes de colunas em `snake_case`: `stock_quantity`, `created_at` e `customer_id`. | Os campos dos models no Prisma e as colunas reais no MySQL estão em `camelCase` (`stockQuantity`, `createdAt`, `customerId`), pois não há `@map` em campos, apenas `@@map` em tabelas. | `prisma/schema.prisma:62:  stockQuantity Int      @default(0)`<br>`prisma/schema.prisma:77:  customerId     String      @db.Char(36)`<br>`prisma/schema.prisma:84:  createdAt      DateTime    @default(now())`<br>`src/modules/orders/order.service.ts:228:        data: { stockQuantity: { decrement: item.quantity } },` |
| **T-04, T-34** | Referiu-se informalmente ao "service de orders". | A classe real chama-se `OrderService` e fica no arquivo `src/modules/orders/order.service.ts`. | `src/modules/orders/order.service.ts:26:export class OrderService {` |
| **T-24** | Referiu-se genericamente ao "middleware de erro centralizado". | A constante exportada chama-se `errorMiddleware` e fica em `src/middlewares/error.middleware.ts`. | `src/middlewares/error.middleware.ts:14:export const errorMiddleware: ErrorRequestHandler = (err, req, res, _next) => {` |
| **T-30, T-59** | Referiu-se a `requireRole` com "role ADMIN obrigatório". | A função `requireRole` fica dentro de `src/middlewares/auth.middleware.ts` (não em um arquivo `requireRole.ts` separado) e sua assinatura real é variádica: `export function requireRole(...roles: AuthUser['role'][]): RequestHandler`, onde `AuthUser['role']` é `'ADMIN' \| 'OPERATOR'`. | `src/middlewares/auth.middleware.ts:9:  role: 'ADMIN' \| 'OPERATOR';`<br>`src/middlewares/auth.middleware.ts:49:export function requireRole(...roles: AuthUser['role'][]): RequestHandler {` |
| **T-36** | Definiu os campos do payload outbound do webhook em `snake_case` (`event_id`, `event_type`, `order_id`, `order_number`, `from_status`, `to_status`, `customer_id`, `total_cents`). | Toda a API REST existente (requests, responses e schemas Zod) e os models do Prisma usam `camelCase` (`orderNumber`, `customerId`, `subtotalCents`, `discountCents`, `totalCents`, `fromStatus`, `toStatus`). | `prisma/schema.prisma:76:  orderNumber    String      @unique @db.VarChar(20)`<br>`prisma/schema.prisma:81:  totalCents     Int`<br>`prisma/schema.prisma:119:  fromStatus   OrderStatus?`<br>`prisma/schema.prisma:120:  toStatus     OrderStatus`<br>`src/modules/orders/order.schemas.ts:12:  customerId: z.string().uuid(),` |
| **T-15, T-29, T-52** | Citou rotas sem prefixo de versão: `GET /orders`, `GET /webhooks/:id/deliveries` e `POST /admin/webhooks/dead-letter/:id/replay`. | Todas as rotas de negócio da aplicação são montadas sob o prefixo `/api/v1` em `src/app.ts` e agrupadas em `src/routes/index.ts` (ex.: `/api/v1/orders`). | `src/app.ts:67:  app.use('/api/v1', buildApiRouter(controllers));`<br>`src/routes/index.ts:28:  router.use('/orders', buildOrderRouter(controllers.orders));` |
| **T-62 vs T-27** | Em `T-62`, Marcos afirmou que "existem usuários que representam o cliente" autenticados via JWT. | No banco (`prisma/schema.prisma`, linhas 25–38 e 40–54) e no token (`src/middlewares/auth.middleware.ts`, linhas 6–25 e 42), `User` e `Customer` são entidades separadas sem campo nem relação entre si (`grep -n -i "customer" prisma/schema.prisma` só encontra `Customer` e `Order`), e `JwtPayload`/`AuthUser` possuem apenas `id`/`sub`, `email` e `role` (`'ADMIN' \| 'OPERATOR'`), sem `customerId`. | `prisma/schema.prisma:25:model User {`<br>`prisma/schema.prisma:34:  createdOrders        Order[]              @relation("OrderCreatedBy")`<br>`prisma/schema.prisma:35:  statusHistoryChanges OrderStatusHistory[] @relation("StatusChangedBy")`<br>`src/middlewares/auth.middleware.ts:42:    req.user = { id: payload.sub, email: payload.email, role: payload.role };` |

---

## Achados do código sem origem na reunião

Observações extraídas exclusivamente da inspeção do código-fonte (não são decisões da reunião) e marcadas como **pendência para o FDD**:

| # | Observação verificada no código | Evidência (`grep -n` / `sed -n` e linhas) | Classificação |
| :--- | :--- | :--- | :--- |
| **1** | **A criação de pedido emite ou não evento:** A reunião tratou apenas da publicação na outbox dentro do método `changeStatus` (`T-34`), mas `OrderService.create` (`src/modules/orders/order.service.ts`, linhas 95–114) também define `status: OrderStatus.PENDING` (linha 99) e grava um registro inicial em `order_status_history` com `fromStatus: null` e `toStatus: OrderStatus.PENDING` (linhas 106–113). | `src/modules/orders/order.service.ts:99:          status: OrderStatus.PENDING,`<br>`src/modules/orders/order.service.ts:106:          history: {`<br>`src/modules/orders/order.service.ts:108:              fromStatus: null,`<br>`src/modules/orders/order.service.ts:109:              toStatus: OrderStatus.PENDING,` | **pendência para o FDD** |
| **2** | **`from === to` e estoque insuficiente abortam a transação antes de qualquer outbox:** Dentro de `OrderService.changeStatus` (`src/modules/orders/order.service.ts`, linhas 131–178), as checagens `if (from === to)` (lança `ConflictError` nas linhas 140–146), `if (!canTransition(from, to))` (lança `InvalidStatusTransitionError` nas linhas 147–149) e `await this.debitStock(tx, order.items)` (chamado na linha 152; lança `InsufficientStockError` na linha 223) executam antes de `tx.order.update` (linha 158) e `tx.orderStatusHistory.create` (linha 159), abortando a transação antes de qualquer gravação na outbox. | `src/modules/orders/order.service.ts:140:      if (from === to) {`<br>`src/modules/orders/order.service.ts:147:      if (!canTransition(from, to)) {`<br>`src/modules/orders/order.service.ts:152:        await this.debitStock(tx, order.items);`<br>`src/modules/orders/order.service.ts:223:      throw new InsufficientStockError(unavailable);` | **pendência para o FDD** |
| **3** | **O `order` da linha 132 traz o status antigo; o payload usa `from` e `to` explícitos:** Na linha 132 de `src/modules/orders/order.service.ts`, `const order = await tx.order.findUnique(...)` é lido no início da transação (logo `order.status` vale `from`, linha 138), `await tx.order.update({ where: { id }, data: { status: to } })` (linha 158) não muta a constante `order` em memória e `refreshed` só é consultado na linha 169; já a assinatura citada em `T-34` (`publishWebhookEvent(tx, order, fromStatus, toStatus)`) recebe `fromStatus` e `toStatus` explicitamente. | `src/modules/orders/order.service.ts:132:      const order = await tx.order.findUnique({`<br>`src/modules/orders/order.service.ts:138:      const from = order.status;`<br>`src/modules/orders/order.service.ts:139:      const to = input.toStatus;`<br>`src/modules/orders/order.service.ts:158:      await tx.order.update({ where: { id }, data: { status: to } });`<br>`src/modules/orders/order.service.ts:169:      const refreshed = await tx.order.findUnique({` | **pendência para o FDD** |
| **4** | **O JWT não tem `customerId` e não existe papel de cliente (só `ADMIN` e `OPERATOR`), então qualquer usuário autenticado poderia gerenciar webhooks de qualquer `customer`:** `AuthUser`/`JwtPayload` (`src/middlewares/auth.middleware.ts`, linhas 6–25 e 42) têm apenas `{ id, email, role: 'ADMIN' \| 'OPERATOR' }` e `User` não possui relação com `Customer` (`prisma/schema.prisma`, linhas 25–38), enquanto `T-27` define que `customer_id` não vem do JWT e `T-50` mantém o CRUD aberto a qualquer role autenticada por enquanto. | `src/middlewares/auth.middleware.ts:9:  role: 'ADMIN' \| 'OPERATOR';`<br>`src/middlewares/auth.middleware.ts:42:    req.user = { id: payload.sub, email: payload.email, role: payload.role };`<br>`prisma/schema.prisma:11:enum UserRole {`<br>`prisma/schema.prisma:12:  ADMIN`<br>`prisma/schema.prisma:13:  OPERATOR` | **pendência para o FDD** |
| **5** | **O worker não sobe sem `DATABASE_URL` e `JWT_SECRET` (`>= 16` caracteres):** `src/config/database.ts` (linha 2) e `src/shared/logger/index.ts` (linha 2) importam `src/config/env.ts`, que executa `loadEnv()` na carga do módulo (linha 27), valida `DATABASE_URL` (linha 7) e `JWT_SECRET` com mínimo de 16 caracteres (linha 8) e encerra o processo com `process.exit(1)` (linha 22) se qualquer uma estiver ausente ou inválida. | `src/config/database.ts:2:import { env } from './env.js';`<br>`src/shared/logger/index.ts:2:import { env } from '../../config/env.js';`<br>`src/config/env.ts:7:  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),`<br>`src/config/env.ts:8:  JWT_SECRET: z.string().min(16, 'JWT_SECRET must be at least 16 characters'),`<br>`src/config/env.ts:22:    process.exit(1);`<br>`src/config/env.ts:27:export const env: Env = loadEnv();` | **pendência para o FDD** |
| **6** | **O logger fixa `base.service = 'order-management-api'`:** Em `src/shared/logger/index.ts` (linha 20), `createLogger()` configura `base: { service: 'order-management-api', env: env.NODE_ENV }`, de modo que os logs do worker sairiam com esse nome ao importar `logger` ou `createLogger()`. | `src/shared/logger/index.ts:20:    base: { service: 'order-management-api', env: env.NODE_ENV },`<br>`src/shared/logger/index.ts:32:export const logger: Logger = createLogger();` | **pendência para o FDD** |
| **7** | **O `redact` atual não cobre campos de `secret` nem o header `X-Signature`:** Em `src/shared/logger/index.ts` (linhas 4–11), `redactPaths` lista apenas `'req.headers.authorization'`, `'req.headers.cookie'`, `'*.password'`, `'*.passwordHash'`, `'*.token'` e `'*.accessToken'`. | `src/shared/logger/index.ts:4:const redactPaths = [`<br>`src/shared/logger/index.ts:5:  'req.headers.authorization',`<br>`src/shared/logger/index.ts:6:  'req.headers.cookie',`<br>`src/shared/logger/index.ts:7:  '*.password',`<br>`src/shared/logger/index.ts:8:  '*.passwordHash',`<br>`src/shared/logger/index.ts:9:  '*.token',`<br>`src/shared/logger/index.ts:10:  '*.accessToken',`<br>`src/shared/logger/index.ts:11:];` | **pendência para o FDD** |
| **8** | **`requireRole` só é usado em `user.routes.ts:15`; as rotas de `orders` usam só `authenticate`:** Em todo o diretório `src/`, `requireRole` só é aplicado na rota `GET /:id` de `src/modules/users/user.routes.ts` (linha 15: `requireRole('ADMIN')`), enquanto `src/modules/orders/order.routes.ts` aplica apenas `router.use(authenticate)` (linha 14). | `src/modules/users/user.routes.ts:14:    authenticate,`<br>`src/modules/users/user.routes.ts:15:    requireRole('ADMIN'),`<br>`src/modules/orders/order.routes.ts:14:  router.use(authenticate);` | **pendência para o FDD** |
| **9** | **Nenhuma transição em `order.status.ts:3–10` tem `PENDING` como destino:** No dicionário `transitions` (`src/modules/orders/order.status.ts`, linhas 3–10), `OrderStatus.PENDING` aparece apenas como chave de origem (linha 4: `[OrderStatus.PENDING]: [OrderStatus.PAID, OrderStatus.CANCELLED]`) e nunca na lista de destinos de nenhum status; logo, um filtro de status que inclua `PENDING` só dispararia na criação do pedido, nunca via `changeStatus`. | `src/modules/orders/order.status.ts:3:const transitions: Readonly<Record<OrderStatus, ReadonlyArray<OrderStatus>>> = {`<br>`src/modules/orders/order.status.ts:4:  [OrderStatus.PENDING]: [OrderStatus.PAID, OrderStatus.CANCELLED],`<br>`src/modules/orders/order.status.ts:5:  [OrderStatus.PAID]: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],`<br>`src/modules/orders/order.status.ts:6:  [OrderStatus.PROCESSING]: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],`<br>`src/modules/orders/order.status.ts:7:  [OrderStatus.SHIPPED]: [OrderStatus.DELIVERED],`<br>`src/modules/orders/order.status.ts:8:  [OrderStatus.DELIVERED]: [],`<br>`src/modules/orders/order.status.ts:9:  [OrderStatus.CANCELLED]: [],`<br>`src/modules/orders/order.status.ts:10:};` | **pendência para o FDD** |
| **10** | **`tests/setup.ts:8–16` limpa as 7 tabelas atuais com `deleteMany()`, em ordem de FK:** O hook `beforeEach` em `tests/setup.ts` (linhas 8–16) executa `deleteMany()` sequencialmente em `orderStatusHistory`, `orderItem`, `order`, `orderNumberSequence`, `product`, `customer` e `user`; tabelas novas precisariam entrar nessa lista. | `tests/setup.ts:8:beforeEach(async () => {`<br>`tests/setup.ts:9:  await prisma.orderStatusHistory.deleteMany();`<br>`tests/setup.ts:10:  await prisma.orderItem.deleteMany();`<br>`tests/setup.ts:11:  await prisma.order.deleteMany();`<br>`tests/setup.ts:12:  await prisma.orderNumberSequence.deleteMany();`<br>`tests/setup.ts:13:  await prisma.product.deleteMany();`<br>`tests/setup.ts:14:  await prisma.customer.deleteMany();`<br>`tests/setup.ts:15:  await prisma.user.deleteMany();`<br>`tests/setup.ts:16:});` | **pendência para o FDD** |
| **11** | **Scripts `dev`/`start` em `package.json` (linhas 11 e 13) e escopo de compilação em `tsconfig.build.json` (linhas 1–11):** Os scripts `dev` (`tsx watch --env-file=.env src/server.ts`, linha 11) e `start` (`node --env-file=.env dist/server.js`, linha 13) usam `--env-file=.env` apontando para `src/server.ts` e `dist/server.js`; já `tsconfig.build.json` define `"rootDir": "./src"` (linha 4), `"outDir": "./dist"` (linha 5), `"include": ["src/**/*.ts"]` (linha 9) e `"exclude": ["node_modules", "dist", "tests", "prisma", "**/*.test.ts"]` (linha 10), de modo que um arquivo `src/worker.ts` entraria no build (`npm run build`, linha 12 de `package.json`). | `package.json:11:    "dev": "tsx watch --env-file=.env src/server.ts",`<br>`package.json:12:    "build": "tsc -p tsconfig.build.json",`<br>`package.json:13:    "start": "node --env-file=.env dist/server.js",`<br>`tsconfig.build.json:1:{`<br>`tsconfig.build.json:2:  "extends": "./tsconfig.json",`<br>`tsconfig.build.json:3:  "compilerOptions": {`<br>`tsconfig.build.json:4:    "rootDir": "./src",`<br>`tsconfig.build.json:5:    "outDir": "./dist",`<br>`tsconfig.build.json:6:    "sourceMap": false,`<br>`tsconfig.build.json:7:    "declaration": false`<br>`tsconfig.build.json:8:  },`<br>`tsconfig.build.json:9:  "include": ["src/**/*.ts"],`<br>`tsconfig.build.json:10:  "exclude": ["node_modules", "dist", "tests", "prisma", "**/*.test.ts"]`<br>`tsconfig.build.json:11:}` | **pendência para o FDD** |
