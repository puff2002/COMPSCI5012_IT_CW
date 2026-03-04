![](data:image/png;base64...)**Assessed Coursework**

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Course Name** | **Internet Technology (M)** | | | | | | | |
| **Coursework Number** | **5 (of 6) – Web Application Implementation Report** | | | | | | | |
| **Deadline** | | **Time:** | **4.30pm** | | **Date:** | **19 March 2026** | | |
| **% Contribution to final course mark** | | **30** | | | **This should take at most these many hours:** | | | **15 (individual)** |
| **Solo or Group ü** | | **Solo** |  | | **Group** | **ü** | | |
| **Submission Instructions** | | **Via Moodle – see Page 4** | | | | | | |
| **Who Will Mark This? ü** | | **Lecturer ü** | | **Tutor ü** | | | **Other** | |
| **Feedback Type? ü** | | **Written ü** | | **Oral** | | | **Both** | |
| **Individual or Generic? ü** | | **Generic** | | **Individual ü** | | | **Both** | |
| **Other Feedback Notes** | |  | | | | | | |
| **Please Note: This Coursework cannot be Re-Done** | | | | | | | | |

**Code of Assessment Rules for Coursework Submission**

Deadlines for the submission of coursework which is to be formally assessed will be published in course documentation, and work which is submitted later than the deadline will be subject to penalty as set out below. The primary grade and secondary band awarded for coursework which is submitted after the published deadline will be calculated as follows:

1. in respect of work submitted not more than five working days after the deadline
   1. the work will be assessed in the usual way;
   2. the primary grade and secondary band so determined will then be reduced by two secondary bands for each working day (or part of a working day) the work was submitted late.
2. work submitted more than five working days after the deadline will be awarded Grade H.

Penalties for late submission of coursework will not be imposed if good cause is established for the late submission. You should submit documents supporting good cause via MyCampus.

**Penalty for non-adherence to Submission Instructions is 2 bands**

|  |
| --- |
| **Marking Criteria** |
| **See Page 9** |

**Web Application Implementation Report (30%)**

1. **Introduction**

The group project is based on the development of a web application of your choosing, as you described it in the Design Specification. You can make changes to the web application you develop but you will need to provide a justification for this if you do.

Your implementation should demonstrate the skills developed during the course. The back end of your application must be built using **Python and Django**, and your project must include appropriate use of **HTML and CSS**.

For the front end, you may choose your approach:

* You may use **Django templates** (server-rendered pages), *or*
* You may use a modern front-end library/framework such as **React** (or similar) and treat Django as an API back end.

You **should** also use **client-side technologies** to enhance interactivity—this can include **JavaScript**, and may include **jQuery** or **AJAX**, but **jQuery is not required** if you use React or other alternatives.

## Core Functionality

Your web application should implement the main functionality described in your Design Specification (or your justified revised version).

At a minimum, your application must:

* Include user authentication (e.g., login/logout and access control)
* Interact with a database model (create/read/update/delete or other meaningful interaction)
* Allow users to input data that is used by the application (e.g., stored, processed, searched, displayed, or used to generate output)

## Front-end Interactivity Requirement

Your application must not be based solely on Python/Django with static pages. There should be clear evidence of front-end/client-side functionality beyond basic server-rendered content.

This can be achieved through at least one of the following:

* JavaScript-driven interactivity (dynamic UI updates, form validation, etc.)
* Asynchronous requests (e.g. AJAX)
* A client-side framework/library used to build an interactive user interface (e.g., React or similar)

## Look and Feel

* Your application should have a **polished, consistent interface** (layout, typography, spacing, navigation should feel intentional rather than clunky).
* The UI must be **responsive** across common screen sizes (mobile, tablet, desktop).
* Use a **responsive CSS framework** (e.g., Bootstrap) *or* an equivalent responsive approach (e.g., well-structured custom CSS using Flexbox/Grid).

## Accessibility

You already created an accessibility plan in the design phase. In this project, you must show how you applied it.

* Choose 2–3 key pages/features (e.g., login + one main feature).
* Implement at least 3 improvements from your accessibility plan.

## Sustainability You must evaluate and improve the sustainability-related performance of your application using an appropriate tool (e.g., [Google Lighthouse](https://developer.chrome.com/docs/lighthouse/overview) or similar).

Your sustainability report should include:

* The **tool(s) used** and the pages tested (at least **2 pages**: homepage + one core feature).
* A **baseline “before” measurement** (scores and/or key metrics, with screenshots/exported report).
* **Any changes you implemented** to improve sustainability-related performance (e.g., reducing page weight, optimising images, removing unused JS/CSS, reducing requests, caching, code-splitting).
* An **“after” measurement** showing the impact, with a short reflection on what improved and why.

## Code

* Code must be **readable, well-organised, and commented where appropriate** (comment intent/decisions, not obvious lines).
* **Avoid duplication**: do not repeat large blocks of logic or markup in views, templates, or components—use reusable helpers/partials/components/utilities.
* **Separation of concerns**: CSS and JavaScript should be kept separate from templates/pages (i.e., avoid inline CSS/JS except where unavoidable and justified).
* Include **helper functions/classes/modules** where appropriate to keep views/components focused.
* Include **unit tests** covering key parts of the application (at minimum: core business logic/models; ideally one view/API endpoint). Provide clear instructions for running tests.

***If using Django templates (server-rendered):***

* Templates should **inherit from a base layout** where appropriate (e.g., base.html).
* URLs must be **named and reverse-resolved** (e.g., {% url 'route\_name' %}), not hard-coded paths.

***If using a front-end framework (e.g., React):***

* Follow equivalent best practices for routing, component reuse, and configuration (e.g., avoid hard-coded absolute URLs; keep API endpoints configurable).

1. **What should be included in the submission**

You must submit:

1. A **Written report** (PDF)
2. Your **Application code** (ZIP of the full project)
3. **Public code repository** (e.g., GitHub/GitLab)
4. **Deployed application** accessible via a public URL

You will add the URLs for **(3) the repository** and **(4) the deployed application** in your **written report.**

**Your report should include the following:**

1. Introduction + Links to code repository and deployed application (max ½ page)

* Give an overview of the application and any adjustments to the design specification.
* Please include the **URLs** to your code repository and your publicly deployed web application here.

1. Updated Design Specification *(max 6 pages)*

* Provide your design specification, highlighting any changes from the original design, and provide a small justification.
* Please include i) user stories, ii) the system architecture diagram, iii) the ER diagram, iv) the sitemap, v) wireframes.
* *Note: You should include your design specification in your report, even if there are no changes from your original submission.*

1. Implementation Highlights (max 2 pages)

* Descibe your implementation, listing all the main components, key features, and demonstrating how the functionality, interactivity, look and feel, and code requirements are achieved.

1. Testing *(max 1 page)*

* Describe the tests you have implemented for your system and demonstrate the system testing results.

1. Accessibility report *(max 1 page)*

* Describe at least 3 improvements you implemented from your accessibility plan, and provide evidence of the improvements (e.g. notes, screenshots).

1. Sustainability report *(max 1 page)*
   * List the tool(s) used and the pages tested for sustainability. Provide a “before” baseline.
   * List the changes made to improve sustainability-related performance, provide an “after” measurement and briefly explain what improved and why.
2. Appendix: Team contributions and AI use statement *(max ½ page)*

# Generative AI (GenAI) use in this assessment

You may use Generative AI to support your work. However, if you use GenAI for anything beyond general background reading, you must **acknowledge how you used it** and **attribute it appropriately**. You remain responsible for the accuracy and originality of our submission.

## When you must acknowledge GenAI use

If you use GenAI to generate content that influences your submission (e.g., debugging support, small code snippets, refactoring suggestions, test ideas, accessibility fixes, or sustainability/performance recommendations), you must include an **AI Use Statement** (see below). Where GenAI provides specific claims or technical guidance, you should verify it using reliable sources (e.g., official documentation) and by testing your implementation.

## Examples

1. **Debugging support**
    You ask GenAI to help interpret an error message or suggest likely causes and fixes (e.g., “Why am I getting CSRF verification failed in Django?” or “Why is this React state not updating?”). You should acknowledge GenAI use and ensure you understand, implement, and test the fix yourself.
2. **Small code snippets / helper functions**
    You ask GenAI to generate or improve a short, self-contained piece of code (e.g., a helper function, a serializer method, a small validation function, a query pattern). You should acknowledge GenAI use and adapt it to your project appropriately.
3. **Refactoring and code quality suggestions**
    You ask GenAI for suggestions to improve readability/structure (e.g., “How can I reduce duplication in these views?” or “Suggest how to structure reusable components”). You should acknowledge GenAI use and ensure the final solution reflects your own design decisions.
4. **Unit test ideas / edge cases**
    You ask GenAI to suggest test cases or edge cases for your existing code (e.g., “What tests should I write for this model method?”). You should acknowledge GenAI use and ensure the tests are relevant, correct, and actually run.
5. **Accessibility implementation guidance**
    You ask GenAI how to implement improvements from your accessibility plan (e.g., labels, keyboard focus, accessible error messages, ARIA for a specific component). You should acknowledge GenAI use and validate the outcome using your chosen checking tool(s).
6. **Sustainability/performance improvement guidance**
    You ask GenAI to help interpret Lighthouse output and suggest changes (e.g., “What does ‘eliminate render-blocking resources’ mean here?”). You should acknowledge GenAI use and provide before/after evidence based on the tool results.

## What is not acceptable

* Submitting GenAI-generated content **without acknowledgement**.
* Including “facts” from GenAI without checking reliability where accuracy matters.
* Presenting GenAI output as if it were an authoritative external source.
* Using GenAI to generate **substantial parts of the application** (e.g., complete pages/components, full features, whole modules, full test suites) and submitting them with only minor edits.
* Asking GenAI to write your **accessibility or sustainability report** in a way that replaces your own analysis and evidence (e.g., “Write my report based on these screenshots/results”).

The university position is that using GenAI in assessments without acknowledgement may constitute academic misconduct (plagiarism).

## AI Use Statement (required if GenAI used beyond background reading)

In your appendix slide, you must include an **“AI Use Statement”** and include any of the following statements that apply:

**Declaration on the use of Generative AI:**

1. We declare that we have not used GenAI in the development of this submission.
2. We declare that we have used GenAI as background reading only (concept explanations and documentation support).
3. We declare that we have used GenAI for copy-editing / improving clarity of language in the report.
4. We declare that we have used GenAI for debugging support (interpreting error messages and suggesting possible fixes), and we implemented and tested the final solution ourselves.
5. We declare that we have used GenAI to generate or refine small, self-contained code snippets (e.g., helper functions/validation), and we adapted them to our project and take responsibility for the final code.
6. We declare that we have used GenAI for refactoring and code-quality suggestions (e.g., reducing duplication, improving structure), and we implemented the changes ourselves.
7. We declare that we have used GenAI to suggest unit test ideas and edge cases, and we wrote/validated the final tests ourselves.
8. We declare that we have used GenAI to support accessibility implementation (e.g., labels, focus handling, keyboard navigation) and validated changes using checking tools (e.g., Lighthouse).
9. We declare that we have used GenAI to support sustainability/performance improvements (e.g., interpreting Lighthouse findings and suggesting optimisations) and validated changes with before/after tool results.
10. We declare that we have used GenAI in another limited way (briefly explain).

**If GenAI was used**, briefly add:

* the tool(s) used (e.g., ChatGPT/Copilot/Gemini)
* what parts were affected (code/tests/report)
* a 1–2 sentence summary of how you ensured correctness (e.g., testing, running lint/tests, verifying against docs)

1. **How to submit**

Your Implementation Report must be saved as a PDF document, and your web application code must be saved in a zip file. One member of the team should submit the pdf document and the zip file via the “Implementation” submission area on the Moodle page of the course. The person making the submission will be required to complete **a Declaration of Originality** on behalf of all team members when submitting via Moodle. If you have used any external sources, be sure to acknowledge them in your submission.

1. **Recommendations for deployment**

There are several platforms that offer free, free-tier, or free-trial hosting suitable for Django apps. Keep in mind that the specifics of these free tiers can change over time, so it’s a good idea to check the latest details on each provider's website. Here are some options:

* [PythonAnywhere](https://eu.pythonanywhere.com/) offers a free beginner’s plan, although it comes with some limitations such as restricted outbound internet access from your apps.
* [Render.com](https://render.com/) offers a free hobby plan, although it comes with some limitations regarding uptime.
* [Replit.com](https://replit.com/) offers a free starter plan, although you may need to configure your environment appropriately.
* Cloud providers like the Google Cloud Platform (GCP) and Amazon Web Services (AWS) provide some free tiers for a limited period or limited usage.

1. **Working in a team**

You should think about how the tasks associated with the development of your team’s web app should be divided. Try to ensure that activities are assigned so that every member of the team can be always involved. A possible breakdown of responsibilities for a team might be (this is just an example, and you should feel free to organize things differently if you prefer):

* user authentication, unit testing
* models
* views
* templates and CSS
* Javascript, AJAX

Please note that under normal circumstances all members in a team will be assigned the same mark.

All members of a team will usually receive the same mark. Where members of a team find the contribution of other members to be unsatisfactory, you are encouraged to resolve the issue internally by negotiation first. However, if this is not possible, the course coordinators should be asked to intervene as soon as possible.

The mark awarded to individual members of the team may be adjusted to reflect the individual’s contribution. **We will be using Deltas as a way of adjusting the team mark in order to arrive at an individual’s mark for the team-based components of the course.**

Each member of a team will be required to submit a form, giving their own as well as their team members’ contributions. A Delta typically adjusts the team mark up or down by 0 or more bands for a given individual according to the contribution. The computation of these Deltas will be informed by the percentage scores that each member of the team will provide, which gives a numerical estimate of the proportion of the overall effort undertaken by each person (including themselves). If in doubt, we will also require evidence of contributions, e.g. emails, GitHub commits, etc. We will also look at the contributions listed in the appendix to validate any adjustments.

**Sample marking scheme**

The following marking scheme is intended to give a broad indication as to how marks will be apportioned. The actual marking scheme used in practice may deviate slightly from this.

|  |  |
| --- | --- |
| **Category** | **Marks** |
|  |  |
| **Deployment** |  |
| Application is deployed and can be used by marker | 3 |
| Repo is public and contains the full project code (reasonable structure, commit history evident). | 2 |
|  |  |
| **Core Functionality** |  |
| Main functionality has been implemented reflecting the design | 5 |
| User authentication is included | 5 |
| Meaningful database interaction is included | 5 |
| User input is processed/stored/searched/displayed meaningfully | 5 |
|  |  |
| **Front-end Interactivity** |  |
| Clear evidence of client-side interactivity beyond static server-rendering | 5 |
|  |  |
| **Look and Feel** |  |
| Polished / refined interface, not clunky | 5 |
| Uses a responsive CSS framework | 5 |
|  |  |
| **Accessibility** |  |
| At least 3 improvements implemented from accessibility plan; evidence provided | 5 |
|  |  |
| **Sustainability** |  |
| Uses an appropriate tool (e.g., Lighthouse) to assess at least two pages and reports before/after results, the changes made, and a brief reflection. | 5 |
|  |  |
| **Code** |  |
| Good implementation, with good separation of concerns | 5 |
| Code is readable, clear and commented where appropriate | 3 |
| Unit tests are included | 2 |
|  |  |
| **Report** |  |
| Good description of design, implementation and testing | 7 |
| Clear writing and structure | 3 |
| **Total** | **70** |

The total mark will be converted to a band which will be the team’s mark for this component of the assessment.
