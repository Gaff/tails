Then /^there is no screenshot in the live user's Pictures directory$/ do
  pictures_directory = "/home/#{LIVE_USER}/Pictures"
  assert($vm.execute(
          "find '#{pictures_directory}' -name 'Screenshot*.png' -maxdepth 1"
        ).stdout.empty?,
         "Existing screenshots were found in the live user's Pictures directory.")
end

Then /^a screenshot is saved to the live user's Pictures directory$/ do
  pictures_directory = "/home/#{LIVE_USER}/Pictures"
  try_for_success(
    timeout: 10,
    message: "No screenshot was created in #{pictures_directory}"
  ) do
    ! $vm.execute(
      "find '#{pictures_directory}' -name 'Screenshot*.png' -maxdepth 1"
    ).stdout.empty?
  end
end

When /^the "(.+)" notification is sent$/ do |title|
  $vm.execute_successfully("notify-send '#{title}'", user: LIVE_USER)
end

Then /^the "(.+)" notification is shown to the user$/ do |title|
  Dogtail::Application.new('gnome-shell').child(title)
end

When /^GNOME shows the "([^"]+)" notification(?: after at most (\d+) seconds)?$/ do |title, timeout|
  timeout = timeout ? timeout.to_i : nil
  gnome_shell = Dogtail::Application.new('gnome-shell')
  notification_list = gnome_shell.child(
    'No Notifications', roleName: 'label', showingOnly: false
  ).parent.parent
  try(timeout: timeout) do
    notification_list.child(title, roleName: 'label', showingOnly: false)
  end
end
