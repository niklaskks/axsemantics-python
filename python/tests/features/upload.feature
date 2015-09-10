# Created by bronsen at 09.09.15
Feature: Upload data and Generate content
  In order to do my work,
  I want to upload data and
  I want to generate content for this data
  Which I then download

  Scenario: Excel file upload
    Given I have a file "test_tv.xlsx"
    And I have the API token "9dc183f2570011e5912775ca8bd11e5d"
    And I have a content project for "tv"
    When I upload the file
    Then I want to see the data in the content project

