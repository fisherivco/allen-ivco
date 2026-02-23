import { MigrateDownArgs, MigrateUpArgs, sql } from '@payloadcms/db-postgres'

export async function up({ db }: MigrateUpArgs): Promise<void> {
  await db.execute(sql`
    ALTER TABLE "company_events" DROP CONSTRAINT "company_events_company_id_companies_id_fk";
    ALTER TABLE "posts" DROP CONSTRAINT "posts_author_id_authors_id_fk";
    ALTER TABLE "posts" DROP CONSTRAINT "posts_category_id_categories_id_fk";

    -- Keep required relationships consistent: NOT NULL + RESTRICT on delete.
    ALTER TABLE "company_events"
      ADD CONSTRAINT "company_events_company_id_companies_id_fk"
      FOREIGN KEY ("company_id")
      REFERENCES "public"."companies"("id")
      ON DELETE restrict ON UPDATE no action;

    ALTER TABLE "posts"
      ADD CONSTRAINT "posts_author_id_authors_id_fk"
      FOREIGN KEY ("author_id")
      REFERENCES "public"."authors"("id")
      ON DELETE restrict ON UPDATE no action;

    ALTER TABLE "posts"
      ADD CONSTRAINT "posts_category_id_categories_id_fk"
      FOREIGN KEY ("category_id")
      REFERENCES "public"."categories"("id")
      ON DELETE restrict ON UPDATE no action;
  `)
}

export async function down({ db }: MigrateDownArgs): Promise<void> {
  await db.execute(sql`
    ALTER TABLE "company_events" DROP CONSTRAINT "company_events_company_id_companies_id_fk";
    ALTER TABLE "posts" DROP CONSTRAINT "posts_author_id_authors_id_fk";
    ALTER TABLE "posts" DROP CONSTRAINT "posts_category_id_categories_id_fk";

    -- Revert to previous behavior from schema_overhaul migration.
    ALTER TABLE "company_events"
      ADD CONSTRAINT "company_events_company_id_companies_id_fk"
      FOREIGN KEY ("company_id")
      REFERENCES "public"."companies"("id")
      ON DELETE set null ON UPDATE no action;

    ALTER TABLE "posts"
      ADD CONSTRAINT "posts_author_id_authors_id_fk"
      FOREIGN KEY ("author_id")
      REFERENCES "public"."authors"("id")
      ON DELETE set null ON UPDATE no action;

    ALTER TABLE "posts"
      ADD CONSTRAINT "posts_category_id_categories_id_fk"
      FOREIGN KEY ("category_id")
      REFERENCES "public"."categories"("id")
      ON DELETE set null ON UPDATE no action;
  `)
}
