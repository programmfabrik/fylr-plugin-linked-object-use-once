class FylrPluginLinkedObjectUseOnce extends BaseConfigPlugin
	getFieldDefFromParm: (baseConfig, fieldName, def) ->
		sort = (a, b) ->
			return a.text.localeCompare(b.text)

		switch def.plugin_type

			when "tan_objecttype"
				field = new ez5.ObjecttypeSelector
					form: label: $$("server.config.parameter.system.fylr_plugin_linked_object_use_once.tan_objecttype.label")
					name: fieldName
					show_name: true
					store_value: "fullname"
					filter: (objecttype) =>
						id = objecttype.table.id()
						if CUI.util.isString(id)
							return false
						mask = Mask.getMaskByMaskName("_all_fields", objecttype.table.id())
						if not mask
							return false

						objecttype.addMask(mask)

						data = objecttype: objecttype.table.name()

						# objecttype must have tag management, and a text field
						if not objecttype.getFields().some((field) => @__filterByTags(field, data))
							return false
						if not objecttype.getFields().some((field) => @__filterByTextField(field, data))
							return false

						return true

			when "main_objecttype"
				field = new ez5.ObjecttypeSelector
					form: label: $$("server.config.parameter.system.fylr_plugin_linked_object_use_once.main_objecttype.label")
					name: fieldName
					show_name: true
					store_value: "fullname"
					filter: (objecttype) =>
						id = objecttype.table.id()
						if CUI.util.isString(id)
							return false
						mask = Mask.getMaskByMaskName("_all_fields", objecttype.table.id())
						if not mask
							return false

						objecttype.addMask(mask)

						data = objecttype: objecttype.table.name()

						if not objecttype.getFields().some((field) => @__filterByTextField(field, data))
							return false

						return true


		return field


	__filterByTextField: (field, data) ->
		# filter for a text field in top level
		if field.table.name() != data.objecttype
			return false

		if data.objecttype == "disbkd_objekt"
			console.log("__filterByTextField", data.objecttype, field)

		if field.__cls == "ez5-text-column"
			return true
		if field.__cls == "ez5-string-column"
			return true
		return false

	__filterByTags: (field, data) ->
		# filter for tag management
		if field.table.name() != data.objecttype
			return false

		if field.__cls == "ez5-tags-field"
			return true
		return false


ez5.session_ready =>
	BaseConfig.registerPlugin(new FylrPluginLinkedObjectUseOnce())

