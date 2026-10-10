// PostHog analytics for the GHSF site (a separate project from TaskMesh).
// The project key is public by design. Until a real key is set, nothing loads.
(function () {
  var KEY = "POSTHOG_PROJECT_KEY";
  var HOST = "https://us.i.posthog.com"; // use https://eu.i.posthog.com if the project is in the EU region
  if (KEY.indexOf("phc_") !== 0) return;

  var s = document.createElement("script");
  s.async = true;
  s.src = HOST.replace(".i.posthog.com", "-assets.i.posthog.com") + "/static/array.full.js";
  s.onload = function () {
    posthog.init(KEY, {
      api_host: HOST,
      person_profiles: "identified_only",
      capture_pageview: true,
      autocapture: true,
      enable_heatmaps: true,
      session_recording: { maskAllInputs: true } // never record what people type in the contact form
    });
  };
  document.head.appendChild(s);
})();
