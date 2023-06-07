// @ts-nocheck
import { afterEach, beforeEach, describe, expect, test } from '@jest/globals';
import puppeteer from "puppeteer";

// CONFIGS
const timeout = 30000;
let browser;
let page;
// --- test attr selector helper (TODO: share test id enums w/ frontend components)
const dti = (testId) => `*[data-test-id="${testId}"]`;


// TESTS
describe("MemberID Widget - Validation", () => {
  // SETUP
  // --- before (reset browser state)
  beforeEach(async () => {
    browser = await puppeteer.launch({ headless: false, slowMo: 10 });
    page = await browser.newPage();
  }, timeout);
  // --- after
  afterEach(() => browser.close());

  // TESTS
  test(
    "Fail",
    async () => {
      await page.goto("http://localhost:7000");
      // init/reset data state
      await page.waitForSelector(dti('setup-sqlite-database-tables'));
      await page.tap(dti('setup-sqlite-database-tables'));
      // Go to validation widget
      await page.waitForSelector(dti('widget-validate-btn'));
      await page.tap(dti('widget-validate-btn'));
      const btnClass = await page.$eval(dti('widget-validate-btn'), (e) => e.className);
      expect(btnClass).toBe('active');
      // Type in valid member ID (too long)
      await page.tap(dti('member-id-validation-input'));
      await page.type(dti('member-id-validation-input'), '23-US-90-07-CB84-AAA');
      await page.tap(dti('member-id-validation-submit'));
      await page.waitForSelector(dti('feedback-message-small'));
      // Expect invalid text
      const feedbackMessageTextOne = await page.$eval(dti('feedback-message-small'), (e) => e.innerText);
      expect(feedbackMessageTextOne.toLowerCase().includes('not valid')).toBe(true);
      expect(feedbackMessageTextOne.toLowerCase().includes('incorrect length')).toBe(true);
      // Delete last 4 chars
      await page.tap(dti('member-id-validation-input'));
      await page.keyboard.press('Backspace');
      await page.keyboard.press('Backspace');
      await page.keyboard.press('Backspace');
      await page.keyboard.press('Backspace');
      await page.tap(dti('member-id-validation-submit'));
      // Expect invalid country code
      const feedbackMessageTextTwo = await page.$eval(dti('feedback-message-small'), (e) => e.innerText);
      expect(feedbackMessageTextTwo.toLowerCase().includes('not valid')).toBe(true);
      expect(feedbackMessageTextTwo.toLowerCase().includes('country code')).toBe(true);
    },
    timeout
  );
  test(
    "Pass",
    async () => {
      await page.goto("http://localhost:7000");
      // init/reset data state
      await page.waitForSelector(dti('setup-sqlite-database-tables'));
      await page.tap(dti('setup-sqlite-database-tables'));
      // Go to validation widget
      await page.waitForSelector(dti('widget-validate-btn'));
      await page.tap(dti('widget-validate-btn'));
      const btnClass = await page.$eval(dti('widget-validate-btn'), (e) => e.className);
      expect(btnClass).toBe('active');
      // Type in valid member ID
      await page.tap(dti('member-id-validation-input'));
      await page.type(dti('member-id-validation-input'), '23-MX-90-07-CB84');
      await page.tap(dti('member-id-validation-submit'));
      await page.waitForSelector(dti('feedback-message-small'));
      const feedbackMessageText = await page.$eval(dti('feedback-message-small'), (e) => e.innerText);
      // Expect valid text
      expect(feedbackMessageText.toLowerCase().includes('valid')).toBe(true);
    },
    timeout
  );
});


describe("MemberID Widget - Generating", () => {
  // SETUP
  // --- before (reset browser state)
  beforeEach(async () => {
    browser = await puppeteer.launch({ headless: false, slowMo: 10 });
    page = await browser.newPage();
  }, timeout);
  // --- after
  afterEach(() => browser.close());

  // TESTS
  test(
    "Pass",
    async () => {
      await page.goto("http://localhost:7000");
      // init/reset data state
      await page.waitForSelector(dti('setup-sqlite-database-tables'));
      await page.tap(dti('setup-sqlite-database-tables'));
      // Go to generation widget
      await page.waitForSelector(dti('widget-generate-btn'));
      await page.tap(dti('widget-generate-btn'));
      const btnClass = await page.$eval(dti('widget-generate-btn'), (e) => e.className);
      expect(btnClass).toBe('active');

      // GENERATE
      // ... first name
      await page.tap(dti('member-id-generating-first-name-input'));
      await page.type(dti('member-id-generating-first-name-input'), 'Jose');
      // ... last name
      await page.tap(dti('member-id-generating-last-name-input'));
      await page.type(dti('member-id-generating-last-name-input'), 'Vasconcelos');
      // ... dob
      await page.tap(dti('member-id-generating-dob-input'));
      await page.type(dti('member-id-generating-dob-input'), '01/01/1961');
      // ... country
      await page.select(dti('member-id-generating-country-select'), 'MX');
      // submit and expect valid message
      await page.tap(dti('member-id-generating-submit'));
      await page.waitForSelector(dti('feedback-message-small'));
      const feedbackMessageText = await page.$eval(dti('feedback-message-small'), (e) => e.innerText);
      expect(feedbackMessageText).toBe('Member ID Generated!');

      // CHECK (bottom list to see if the member ID was added (and has correct year/country))
      await page.waitForSelector(`${dti('member-id-list-ul')} > li`);
      const memberIds = await page.$$eval(`${dti('member-id-list-ul')} > li`, options => {
        return options.map(option => option.innerText);
      })
      const recentMemberId = memberIds[0];
      expect(recentMemberId.includes('23')).toBe(true);
      expect(recentMemberId.includes('MX')).toBe(true);
      expect(recentMemberId.includes('61')).toBe(true);

      // VALIDATE
      await page.waitForSelector(dti('widget-validate-btn'));
      await page.tap(dti('widget-validate-btn'));
      const btnClassValid = await page.$eval(dti('widget-validate-btn'), (e) => e.className);
      expect(btnClassValid).toBe('active');
      // Type in valid member ID
      await page.tap(dti('member-id-validation-input'));
      await page.type(dti('member-id-validation-input'), recentMemberId); // putting in what we generated
      await page.tap(dti('member-id-validation-submit'));
      await page.waitForSelector(dti('feedback-message-small'));
      const feedbackMessageValidationText = await page.$eval(dti('feedback-message-small'), (e) => e.innerText);
      // Expect valid text
      expect(feedbackMessageValidationText).toBe('Member ID is valid. Member ID is in use.');
    },
    timeout
  );
});

