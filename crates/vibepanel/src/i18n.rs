//! Translations.
//!
//! UI strings are marked with `tr!` (from the `tr` crate) and looked up through
//! glibc's gettext. The compiled catalogs (`po/locale/<lang>/vibepanel.mo`) are
//! embedded in the binary and written to `$XDG_RUNTIME_DIR` at startup, so
//! translations work regardless of how vibepanel was installed.
//!
//! The language follows the usual gettext environment (`LANGUAGE`, `LC_ALL`,
//! `LC_MESSAGES`, `LANG`). Missing or unknown languages fall back to English.

use std::path::PathBuf;

/// gettext domain. `tr!` derives it from the crate name, so it must match.
const DOMAIN: &str = "vibepanel";

/// Compiled catalogs, keyed by gettext language name.
const CATALOGS: &[(&str, &[u8])] = &[("zh_CN", include_bytes!("../po/locale/zh_CN/vibepanel.mo"))];

/// Install the embedded catalogs and bind the gettext domain.
///
/// Errors are non-fatal: on failure the UI simply stays in English.
pub fn init() -> std::io::Result<()> {
    // Only the per-user runtime dir: a shared fallback like /tmp would let other
    // users plant symlinks or their own catalogs.
    let base = std::env::var_os("XDG_RUNTIME_DIR")
        .map(PathBuf::from)
        .ok_or_else(|| std::io::Error::other("XDG_RUNTIME_DIR is not set"))?
        .join(DOMAIN)
        .join("locale");

    for (lang, bytes) in CATALOGS {
        let dir = base.join(lang).join("LC_MESSAGES");
        std::fs::create_dir_all(&dir)?;
        // Replace atomically: other running instances have the old file mmapped,
        // and truncating it in place would crash them.
        let path = dir.join(format!("{DOMAIN}.mo"));
        let tmp = path.with_extension(format!("mo.{}", std::process::id()));
        std::fs::write(&tmp, bytes)?;
        std::fs::rename(&tmp, &path)?;
    }

    let base = base
        .to_str()
        .ok_or_else(|| std::io::Error::other("non UTF-8 locale directory"))?;
    gettextrs::bind_textdomain_codeset(DOMAIN, "UTF-8")?;
    tr::tr_init!(base);
    Ok(())
}
