@product @doc
Feature: Tails documentation

  Scenario: The Tails documentation launcher on the desktop works
    Given I have started Tails from DVD without network and logged in
    When I double-click on the Tails documentation launcher on the desktop
    Then the documentation viewer opens the "Getting started" page

  #15321
  @fragile
  Scenario: The Report an Error launcher will open the support documentation
    Given I have started Tails from DVD without network and logged in
    When I double-click on the Report an Error launcher on the desktop
    Then the documentation viewer opens the "Support" page
