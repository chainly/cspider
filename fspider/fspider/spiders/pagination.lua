treat = require("treat")

function main(splash, args)
  local results = {}
  assert(splash:go(splash.args.url))
  assert(splash:wait(3))
  -- local title = splash:evaljs("document.title")
  -- return results["title"] = title
  local links = splash:select_all('a')
  for i, a in ipairs(links) do
    -- https://developer.mozilla.org/en-US/docs/Web/API/Element
    -- print(i, a.node.attributes, a.node.text())
    -- https://blog.csdn.net/cws1214/article/details/14452879
    --for k, v in pairs(a.node.attributes) do
    --  print(k, v)
    --end
    
    -- but this may contain timestamp/auth .etc!!!
    local entries = treat.as_array({})
    splash:on_request(function(request)
        table.insert(entries, request.info)
    end)
    
    if a.node.text() == splash.args.next then
      results["next"] = a.node.text()
        -- find first three page
        -- @TODO: find a common way!
        i = 0
        while (i < 3) do
          assert(a:mouse_click{})
          assert(splash:wait(5))
          local links = splash:select_all('a')
          results["links"] = {}
          for i, a in ipairs(links) do
            txt = a.node.attributes.title or a.node.text()
            results["links"][txt] = a.node.attributes.href
          end
        end
        -- https://stackoverflow.com/questions/1758991/how-to-remove-a-lua-table-entry-by-its-key
        results["links"][splash.args.next] = nil
    end
    
    results["entries"] = entries
  end

  return results
end