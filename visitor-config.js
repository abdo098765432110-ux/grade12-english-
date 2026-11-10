/* ==========================================================================
   The visitor register: where it is saved (Supabase, free plan).

   Fill in the two values from your Supabase project
   (Project Settings → API Keys / Data API), then upload this file:

     url  the Project URL, like "https://abcdefghijklmnop.supabase.co"
     key  the PUBLISHABLE key ("sb_publishable_…") — or the legacy "anon public" key.

   These two values are public by design: every visitor's browser needs them,
   and the database's Row Level Security (tools/visitors/supabase-setup.sql)
   is what protects the register: with this key a student can only add his
   own name; he can not read, change or delete anything.

   NEVER put the "secret" key ("sb_secret_…") or the "service_role" key here
   (or anywhere in the website files): visitor.js refuses to use them.

   While url or key is empty, the registration screen is switched off and the
   website works as before.
   ========================================================================== */
window.G12_VISITORS = {
  url: '',
  key: ''
};
